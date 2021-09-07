import sys
sys.path.append("/Users/xushuzhen/Project/test/piggybank")

from chia.types.condition_opcodes import ConditionOpcode
from chia.types.spend_bundle import SpendBundle
import pytest
from piggybank_drivers import (
    create_piggybank_puzzle,
    solution_for_piggybank,
    piggybank_announcement_assertion
)
from cdv.test import setup as setup_test


# 测试标准交易
# 需要注意的点：生成一个货币，这个货币中至少要有1mojo（ 1 mojo = XCH的万亿分之一）

class TestStandardTransation:
    @pytest.fixture(scope="function")
    async def setup(self):
        #  (network全节点网络，模拟区块链网络的交互）
        # （alice和bob是两个人的钱包）
        network, alice, bob = await setup_test()
        await network.farm_block()
        yield network, alice, bob

    # 测试函数 生成和花费存钱罐
    async def make_and_spend_piggybank(self, network, alice, bob, CONTRIBUTION_AMOUNT):
        # alice作为农民，在区块链网络上获得一些钱（就是给alice点钱，用于测试）
        await network.farm_block(farmer=alice)

        # 生成一个存钱罐，存钱罐的最大额度1000000000000 mojo，接收地址是bob
        piggybank_coin = await alice.launch_smart_coin(
            create_piggybank_puzzle(1000000000000, bob.puzzle_hash))

        # alice钱包中拿出的钱，做成一个货币
        contribution_coin = await alice.choose_coin(CONTRIBUTION_AMOUNT)

        # 消耗存钱罐货币的操作
        piggybank_spend = await alice.spend_coin(
            # 消耗的是存钱罐货币
            piggybank_coin,
            # 是否直接发送到区块链网络，这里不推送到公网上
            pushtx=False,
            # 消耗货币的结果，或者存钱的结果（消耗货币-，存钱+）
            args=solution_for_piggybank(
                piggybank_coin.as_coin(), CONTRIBUTION_AMOUNT),
        )
        # 消费alice钱包货币的操作
        contribution_spend = await alice.spend_coin(
            # 上面已经从alice钱包中拿出的钱
            contribution_coin,
            # 是否直接发送到区块链网络，这里不推送到公网上
            pushtx=False,
            # 金额计算，钱包里的总额，减去存款金额
            amt=(contribution_coin.amount - CONTRIBUTION_AMOUNT),
            # 货币更新，更新为花钱之后的余额
            custom_conditions=[
                [
                    ConditionOpcode.CREATE_COIN, contribution_coin.puzzle_hash,
                    (contribution_coin.amount - CONTRIBUTION_AMOUNT)
                ],
                # 对花钱操作做绑定，确认花钱操作
                piggybank_announcement_assertion(
                    piggybank_coin.as_coin(), CONTRIBUTION_AMOUNT)
            ]
        )

        # 把要发到网络上的货币记录打包（存钱罐的记录，alice的记录）
        combined_spend = SpendBundle.aggregate(
            [piggybank_spend, contribution_spend])

        # 把打包好的记录发送到网络上（这个网络是cdv测试功能提供的模拟网络）
        # （生成包和发送包的过程，和官方教程第九集后面写的json，是一个过程；只不过教程里写了个json手动实现了以下）
        result = await network.push_tx(combined_spend)
        return result

    # 以下为测试用例

    # 存款，但存款没有达到预设的最大额度
    # 钱保留在存钱罐里

    @pytest.mark.asyncio
    async def test_piggybank_contribution(self, setup):
        network, alice, bob = setup
        try:
            # 创建一个存钱罐，存500mojo
            result = await self.make_and_spend_piggybank(network, alice, bob, 500)
            # 检测result中是否有error，有就是一个错误
            assert "error" not in result

            # 以为货币中至少有1mojo，所以存钱罐中应该有501余额
            # 存钱罐的接收地址，应该和创建存钱罐时输入的bob的地址一致
            filtered_result = list(filter(
                lambda addition:
                    (addition.amount == 501) and
                    (addition.puzzle_hash == create_piggybank_puzzle(
                        1000000000000, bob.puzzle_hash).get_tree_hash()),
                result["additions"]))
            # 判断满足filtered_result条件的货币，有且只有1个，如果不是1个就是错误
            assert len(filtered_result) == 1
        finally:
            await network.close()

    # 存款，但存款达到预设的最大额度
    # 达到最大额度，钱到存钱罐柯里化时配置的地址中去
    # 并且生成新的存钱罐
    @pytest.mark.asyncio
    async def test_piggybank_completion(self, setup):
        network, alice, bob = setup
        try:
            # 创建一个存钱罐，存1000000000000mojo，也就是存1txch
            result = await self.make_and_spend_piggybank(network, alice, bob, 1000000000000)
            # 检测result中是否有error，有就是一个错误
            assert "error" not in result

            # 检测新的存钱罐，新的存钱罐余额为0
            filtered_result = list(filter(
                lambda addition:
                    (addition.amount == 0) and
                    (addition.puzzle_hash == create_piggybank_puzzle(
                        1000000000000, bob.puzzle_hash).get_tree_hash()),
                result["additions"]))
            assert len(filtered_result) == 1

            # 检测bob账户货币，余额应为1000000000001mojo
            filtered_result = list(filter(
                lambda addition:
                    (addition.amount == 1000000000001) and
                    (addition.puzzle_hash == bob.puzzle_hash),
                result["additions"]))
            assert len(filtered_result) == 1
        finally:
            await network.close()

    # 偷窃，从群钱罐里偷钱
    @pytest.mark.asyncio
    async def test_piggybank_stealing(self, setup):
        network, alice, bob = setup
        try:
            # 创建一个存钱罐，存-100mojo
            result = await self.make_and_spend_piggybank(network, alice, bob, -100)
            # 存负数肯定是错误的，所以如果结果中没有error，就是错误
            assert "error" in result
            assert "GENERATOR_RUNTIME_ERROR" in result["error"]
        finally:
            await network.close()