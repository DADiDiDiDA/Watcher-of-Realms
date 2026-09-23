仅自用存档，各项任务里面有介绍（欢迎直接copy）

名字懒得改了，反正只能完成日常活跃度任务

注意：模拟器最好改成720 1080
注意：打开自动战斗-后台战斗
注意：打开矮人商城-金币购买不提示
注意：修改背包-装备-排序方式-装备等级-升序排列



注意：pc预启动需要安装 Python 依赖

在你要用来运行 pretask 的 Python 环境里执行：

pip install pyautogui pygetwindow psutil opencv-python

需要修改的东西只有三处（每次更新都要重改；如果只用模拟器不用管）：

pretask.exec → 改成目标电脑的 Python 路径

pretask.args → 改成目标电脑的脚本路径

agent\\launch\_via\_launcher.py 里的 LAUNCHER\_PATH → 改成目标电脑的启动器路径



没发现bug，暂时不打算改了

