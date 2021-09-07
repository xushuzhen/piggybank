# piggybank 对chia官方演示的消化


## 运行环境、log等级配置、基本信息查看

1. python虚拟环境（python3）
   
    ```
    python -m venv venv
    . ./venv/bin/activate
    ```

2. 直接pip安装chia_dev_tools 或 clone chia官方的git进行安装
   
    ```
    pip install chia_dev_tools
    ```

   或

    ```
    git clone https://github.com/Chia-Network/chia-blockchain.git
    cd chia-blockchain
    pip install .
    ```

3. 如果需要查看完整log，可以把log等级改为info
   
   ```
   vi ~/.chia/mainnet/config/config.yaml
   ```

   查看log

   ```
   tail -f ~/.chia/mainnet/log/debug.log
   ```

4. 切换到chia测试网络
   
   ```
   chia configure -t true
   ```

5. 启动chia钱包(会自动启动全节点)
   
   ```
   chia start wallet
   ```

6. 查看chia进程
   
   ```
   ps -ef |grep chia
   ```

7. 查看chia status
   
   ```
   chia show -s
   ```

8. 查看钱包状态
   
   ```
   chia wallet show
   ```

9. 查看钱包地址
   
   ```
   chia keys show
   ```

## piggybank智能币基本操作

1. 生成条件码文件(库文件)
   
   ```
   cdv clsp retrieve condition_codes
   ```

2. 在piggybank.clsp中引用库文件

3. 编译货币
   
   ```
   cdv clsp build -i ./include ./piggybank.clsp
   ```

4. 反汇编查看货币代码
   
   ```
   cdv clsp disassemble ./piggybank.clsp.hex
   ```

5. 用官方工具把钱包接收地址转化成puzzle_hash，供存钱罐货币使用
   
   （感觉puzzle_hash像是钱包地址的别名）

   网址：https://www.chiaexplorer.com/tools/address-puzzlehash-converter

6. 柯里化生成存钱罐货币的treehash
   
   （中间步骤，用于生成txch货币地址）
   （-a跟的是参数）
   
   ```
   cdv clsp curry piggybank.clsp.hex -a 1000 -a your_puzzle_hash --treehash
   ```

7. encode成测试网络txch前缀的货币地址
   
   ```
   cdv encode your_treehash --prefix txch
   ```

8. 转账
   
   （必须在同步完全部区块之后，才能进行转账操作）

   ```
   chia wallet send -a0 -t your_货币地址 --override
   ```

9. 查看转账信息
    
    ```
    cdv rpc coinrecords --by puzhash your_puzzle_hash
    ```

## 测试

（以下都在piggybank目录下执行）

1. 用python编写驱动dao文件piggybank_drivers.py
   
2. 初始化测试用例(或直接写)
   
   ```
   cdv test --init
   ```

3. 查看所有未运行的测试
   
   ```
   cdv test --discover
   ```

4. 执行测试
   
   ```
   cdv test
   ```


## 祝你运行顺利