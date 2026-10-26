# 按图找玩具视频 · toy-image-video-search

给支持图片理解、联网搜索和浏览器核验的 Codex 提供一个 skill：从玩具图片识别商品，查找 YouTube / TikTok 开箱、演示及评测，交付视频链接与同款依据。

默认玩具优先、不限语言、免费优先，只返回链接，不下载媒体。不是独立的自动识图应用：识图与视频画面核验由 agent 执行；Python 脚本负责检索候选。

## 安装

Windows PowerShell（需要 Git 和 Python）：

```powershell
$skillRoot = if ($env:CODEX_HOME) { Join-Path $env:CODEX_HOME 'skills' } else { Join-Path $env:USERPROFILE '.codex/skills' }
New-Item -ItemType Directory -Path $skillRoot -Force | Out-Null
git clone https://github.com/2980415193-tech/toy-image-video-search.git (Join-Path $skillRoot 'toy-image-video-search')
python -m pip install --upgrade yt-dlp
```

macOS / Linux：

```bash
git clone https://github.com/2980415193-tech/toy-image-video-search.git "${CODEX_HOME:-$HOME/.codex}/skills/toy-image-video-search"
uv tool install yt-dlp
```

目标目录已存在时不要覆盖；在现有仓库中用 `git pull --ff-only` 更新。也可下载仓库 ZIP 后解压。

将整个仓库放到 `$CODEX_HOME/skills/toy-image-video-search`；未配置 CODEX_HOME 时使用 `~/.codex/skills/toy-image-video-search`。目录内应直接包含 SKILL.md。

需要 Python 3.10+、可访问 YouTube 的网络，以及 agent 可用的联网搜索/浏览器工具。

```powershell
python -m pip install --upgrade yt-dlp
```

也可使用 `uv tool install yt-dlp`。不需要安装两个版本。

## 使用

向 Codex 发送产品图，并输入：

> 使用 $toy-image-video-search 找这款产品的 YouTube 和 TikTok 视频，给出同款链接及匹配依据。

脚本单独检索示例（从仓库目录运行）：

```powershell
python scripts/search_youtube.py --query "toy brand model unboxing" --limit 5 --output candidates.json
```

结果中的视频默认标记为待核验。只有进一步核对画面、型号及配件，才能认定同款。

## 能力边界

- YouTube 使用 yt-dlp 搜索，不需要 API key；网络错误或平台限制可能导致失败。
- TikTok 使用 agent 的网页搜索和浏览器，不是 yt-dlp 全站搜索。登录限制和搜索引擎收录不全可能导致没有可交付结果。
- 无 Nexscope key 时，仍可识图提取关键词并搜索。图片反查接口是可选增强，需要公开图片 URL；不会自动把附件上传公共图床。
- Nexscope 两个适配接口已实现，但需要自己的账户和 key 联调；免费余额与接口收费需先确认。详见 [接入说明](references/nexscope.md)。不要提交真实 key。
- 视频链接及同款判断不授予素材转载或商业使用权。

## 文件

- [SKILL.md](SKILL.md)：识图、双平台搜索、匹配核验流程。
- [scripts/search_youtube.py](scripts/search_youtube.py)：只读取候选元数据。
- [scripts/nexscope_request.py](scripts/nexscope_request.py)：可选 API 请求，默认仅输出请求计划。

Nexscope 接口参考 [官方电商 skills 仓库](https://github.com/nexscope-ai/nexscope-ecommerce-skills) 和 [官方接入文档](https://www.nexscope.ai/help/skills-external-access)；本仓库提供独立的组合流程和适配脚本，不是 Nexscope 官方项目。
