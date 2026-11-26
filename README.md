# LAAP · CA 案卷阅读桥（只读）

本仓只做一件事：给**没有终端、没有 GitHub 连接器**的 CA 接任席位提供可直读的裁定案卷。
**只读**。不是工作仓，不接受任何写入；正式工作仓为私有仓，由 A01 落盘、签章、推送。

## 文件映射

| 桥内文件（`case/` 目录） | 正式仓对应件 |
|---|---|
| identity.md | 00_governance/_board/CA_首席顾问/CA_身份卡.md |
| handoff.md | 00_governance/_board/CA_首席顾问/CA_HANDOFF.md |
| revival.md | 00_governance/_board/CA_首席顾问/CA_复活手册.md |
| open_items.tsv | 00_governance/_board/CA_首席顾问/CA_OPEN_ITEMS.tsv |
| reins.md | 00_governance/_board/CA_首席顾问/CA_缰绳_主线锚.md |
| rein_check.py | 00_governance/_board/CA_首席顾问/CA_rein_check.py |
| card_097.md | 00_governance/_board/A01_to_CA_20261127_097_口令_请核五件并采信v2.md |
| ruling_90.md | 00_governance/_board/CA_to_A01_20261126_90_裁89号三问.md |
| rep_092..096.md | 00_governance/_board/A01_to_CA_20261127_09{2,3,4,5,6}_*.md |
| template_card_v1.1.md | 00_spec_口令卡固定格式_模板_v1.1_20261117.md |

## 阅读顺序

1. `case/identity.md` — 你是谁、权界、禁项
2. `case/handoff.md` — 上一任留下的事实与未结项（截至 2026-11-26 10:25）
3. `case/card_097.md` — 本次要你裁的五问（唯一任务入口）
4. `case/rep_092..096.md` — 五问的支撑件
5. `case/template_card_v1.1.md` — 回件格式，必须照此十八节
6. `case/ruling_90.md` — 上一份裁定，看你前任怎么落笔
7. `case/open_items.tsv` / `case/reins.md` — 未结与主线锚

## 纪律

- 本仓内容为只读快照，可能与正式仓存在数分钟差异；以正式仓 sha16 为准。
- 不索取、不使用任何 GitHub token。接任席位不写仓，回件以文本交回。
- 不对外引用、不转存、不喂给第三方服务。
