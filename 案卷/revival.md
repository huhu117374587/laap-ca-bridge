# CA_复活手册（新窗口 10 分钟满血复活）

## 0 缰绳（先于一切）
读 `CA_缰绳_主线锚.md`；跑 `CA_rein_check.py` 三模式；回复第0节=其输出；RED 则首条拉回令。

## 1 前置
- 大王把 GitHub 连接器授权给 **Bnan1985**，范围 All repositories（曾因授权到错账号推不上去；已修复）。
- **不使用任何明文 token**；代理 403 就如实报告，不绕。

## 2 接入
1. `mcp__claude-code-remote__add_repo`（owner=`Bnan1985`, repo=`laap-bnan`, access=`push`），按返回的克隆命令浅克隆，再 `register_repo_root`。
2. 读序：`00_governance/_board/CA_首席顾问/CA_身份卡.md` → `CA_HANDOFF.md` → 最新的 `_board/A01_to_CA_*.md` → 它指向的 `60_ledger/05_northstar/CA_PACK/*` 与 `CLOSURE_*`。
3. 项目记忆：`/projects/01a1cf57-153c-722f-8a39-8f9860070643/areas/laap-ca-role.md` 已含角色摘要。

## 3 关键复算命令（令面）
```bash
cd <仓库根>
shasum -a 256 40_instrument/北极星仪器/ns001/{adapter_v3_budget,practice,detector}.py | cut -c1-16   # 对照 60_ledger/05_northstar/FREEZE.tsv
./60_ledger/05_northstar/VERIFY_ORDER.sh                                                              # ORDER_SHA8=8a64d6ff
# 528+3072=3600 平账、E2/E4 计数、撤销回放脚本：见 CA_AUDIT_NS_20261113_02.md §五
```
冻结 sha16：ENGINE `2135a55563d9e83e` / PRACTICE `50246a4173516cdc` / DETECTOR `70088e66e1c23670`。

## 4 数据结构速记
- 答案 `NS001/runs/eval/<world>/answers_F*.jsonl`：`{qid, decision, polarity, trace:{chunks:[…]}, input_sha}`。
- 快照 `NS001/stores_eval/<world>/snap_F*.jsonl`：`{chunk_id, a, c, pol, src_step}`，`chunk_id=sha256("a|c|pol")[:8]`。
- 探测 `NS001/runs/eval/<world>/detectors/detect_F{a}_F{b}/{events,rejects}.tsv`；拒收码 E1_INPUT_DIFF/E2_NOT_SUPERSET/E2_TARGET_LEAK/E3_NO_FLIP/E4_NOT_REVERSIBLE/E5_NO_CLASS。
- 汇总 `60_ledger/05_northstar/NS-07/summary_table.tsv`（事件数=第 11 列，拒收原因计数=第 12 列）。

## 5 送达核验（不用 token）
推送后：`git fetch origin && git diff --stat HEAD origin/main` 应为空，并 `git show origin/main:<路径> | shasum -a 256` 与本地一致。A01 的 `70_check/prepush_gate.py` 需 token，我不用。

## 6 每次对话收尾必做（自动，不等提醒）
1. 在 `CA_HANDOFF.md` "日志"追加一行；必要时覆盖"当前状态"。
2. `git add` 仅 `00_governance/_board/CA_*`；提交说明末尾加归属行；推送并按 §5 核验。
3. 同步项目记忆里的角色摘要（仅当角色/规则变化）。
