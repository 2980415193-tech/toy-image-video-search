# Nexscope 可选接入

2026-10-26 核验来源：
- https://www.nexscope.ai/help/skills-external-access
- https://github.com/nexscope-ai/nexscope-ecommerce-skills/tree/main/ecommerce-amazon-search-by-image
- https://github.com/nexscope-ai/nexscope-ecommerce-skills/tree/main/ecommerce-tiktok-video-search

官方说明外部调用消耗积分。2026-10-26 的 https://www.nexscope.ai/pricing 标示新账号赠送 1,000 积分、有效期 3 天、不需信用卡，包含电商 Data APIs；具体账户与两个目标接口仍未验证。让用户在官网注册，https://www.nexscope.ai/seller/api-access?tab=api-keys 创建 key，并在 Data 页确认接口预计积分和赠送余额。不要让用户在聊天里发送 key；在本机环境设置 NEXSCOPE_API_KEY，NEXSCOPE_PROXY_BASE=https://api.nexscope.ai/。官方条款可能变化，使用前核验；免费试用不等于永久免费。

已核对源码使用 Bearer 认证；仓库 api.md 部分旧环境变量及认证示例与源码不一致，以当前官方接入文档与账户示例为准。

本 skill 的 scripts/nexscope_request.py 提供两个有限接口，使用 Python 标准库。默认仅生成请求计划，不联网；只有账户免费额度已核实才传 --free-credits-confirmed。这个参数是操作确认，不会查询或强制服务器计费余额。每次仅一次请求，无自动重试、无自动翻页。响应 cost 是耗时，不能当积分。

## 图片反查

POST /api/v1/tools/research/amazon/searchByImage

参数文件示例：
```json
{"imageUrl":"https://example.com/product.jpg","amazonDomain":"amazon.com","aggregateByKeepaData":false}
```

imageUrl 必须是可公开访问的真实图片网址。聊天附件、本地路径、data URL 不能直接传入。不自动把图片上传公共图床；优先让用户提供已有商品图片链接，或继续识图关键词路径。

## TikTok 视频

POST /api/v1/tools/research/echotik/listVideo

参数文件示例：
```json
{"region":"US","productId":"真实的TikTok商品ID","pageSize":10,"pageNum":1}
```

必须先从 TikTok 商品候选链接/详情中取得该站点 productId。Amazon ASIN 不是此 ID；此接口没有关键词搜索参数。无法确认 TikTok 商品 ID 时，用免费网页搜索，不调用宽泛地区榜单冒充同款搜索。

执行示例：
`python scripts/nexscope_request.py amazon-image --params params.json --output response.json`

检查请求计划后，仅在免费额度已确认时加 `--free-credits-confirmed`。无 key 只能测试准备阶段，不能声称 API 已联调。HTTP 成功后仍需外层数字 code 严格等于 0；HTTP 200、缺失 code、字符串 0 都不能判成功。商品或视频字段从 data 中读取，officialUrl 是视频链接字段之一。错误响应保留到本地供诊断，但不输出 key。不要运行上游反馈接口或发送用户对话。
