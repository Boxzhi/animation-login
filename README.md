# 抚州公用水务 Home Assistant 插件

本仓库新增了一个 `custom_components/fuzhou_water` 自定义集成，用于通过抚州公用水务微信公众号接口查询账单与欠费信息。集成需要你在 Home Assistant 的集成界面中填写以下抓包参数：

- `Authorization`（OpenID）
- `Token`（JWT）
- 用户编号、用户姓名
- 起始年月与结束年月（YYYYMM）

集成会提供以下传感器：

- Latest Bill Amount（最新账单金额）
- Latest Usage（最新用水量）
- Arrears Amount（欠费金额）
