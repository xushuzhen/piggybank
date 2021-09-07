import sys
sys.path.append("/Users/xushuzhen/Project/test/piggybank")
from chia.types.blockchain_format.coin import Coin
from chia.types.blockchain_format.sized_bytes import bytes32
from chia.types.blockchain_format.program import Program
from chia.types.condition_opcodes import ConditionOpcode
from chia.util.ints import uint64
from chia.util.hash import std_hash

from clvm.casts import int_to_bytes
from cdv.util.load_clvm import load_clvm

# 载入chialisp虚拟机
PIGGYBANK_MOD = load_clvm("piggybank.clsp", "piggybank")
# PIGGYBANK_MOD = load_clvm("piggybank.clsp", "cdv.examples.clsp")


# 创建存钱罐
def create_piggybank_puzzle(amount, cash_out_puzhash):
    return PIGGYBANK_MOD.curry(amount, cash_out_puzhash)


# 存钱
def solution_for_piggybank(pb_coin, contribution_amount):
    return Program.to(
        [pb_coin.amount, (pb_coin.amount + contribution_amount), pb_coin.puzzle_hash])


# 验证条件
def piggybank_announcement_assertion(pb_coin, contribution_amount):
    return [
        ConditionOpcode.ASSERT_COIN_ANNOUNCEMENT,
        std_hash(pb_coin.name() + int_to_bytes(pb_coin.amount + contribution_amount))]
