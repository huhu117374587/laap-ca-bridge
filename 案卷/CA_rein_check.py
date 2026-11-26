#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CA_rein_check.py — CA「缰绳」机检（只读、零网络、零模型、确定性）

用法（在仓根执行）：
  python3 -I 00_governance/_board/CA_首席顾问/CA_rein_check.py --card <卡.md>   # 单卡
  python3 -I .../CA_rein_check.py --sweep [--since ISO]                          # 扫 A01 新卡 + 章台账
  python3 -I .../CA_rein_check.py --open                                         # 列 CA 交办项到期情况
退出码：0=GREEN 1=AMBER 2=RED（--sweep 取各卡最大值）
配置全部取自 CA_缰绳_主线锚.md 的 ```rein-config 块；本脚本只是启发式预警，判词由人工写。
"""
import argparse, hashlib, os, pathlib, re, subprocess, sys
from datetime import datetime, timezone, timedelta

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]
ANCHOR = HERE / "CA_缰绳_主线锚.md"
OPEN = HERE / "CA_OPEN_ITEMS.tsv"
MLOG = ROOT / "00_governance/_board/MLINE_LOG.tsv"
TZ = timezone(timedelta(hours=8))


def cfg():
    t = ANCHOR.read_text(encoding="utf-8")
    m = re.search(r"```rein-config\n(.*?)```", t, re.S)
    d = {}
    for ln in m.group(1).splitlines():
        if "=" in ln:
            k, v = ln.split("=", 1)
            d[k.strip()] = v.strip()
    d["BANNED_WORDS"] = [x for x in d["BANNED_WORDS"].split(",") if x]
    d["EXEMPT_MARKERS"] = [x for x in d["EXEMPT_MARKERS"].split(",") if x]
    d["ALLOWED_ORDERS"] = [x for x in d["ALLOWED_ORDERS"].split(",") if x]
    d["HEADER_REQUIRED"] = [x for x in d["HEADER_REQUIRED"].split(",") if x]
    return d


def sha16(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()[:16]


def head_of(txt):
    m = re.search(r"^##\s", txt, re.M)
    return txt[: m.start()] if m else txt


def _ca_issued(num):
    """CA-OP-NS-<num> 是否在 CA_to_A01_*.md 的「令号：」行出现过（CA 真签发）"""
    import glob
    if int(num) < 40:   # 40 号前为历史令号，不追溯
        return True
    base=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    for f in glob.glob(os.path.join(base,"CA_to_A01_*.md"))+glob.glob(os.path.join(base,"CA_to_*_*.md")):
        try:
            head=open(f,encoding="utf-8").read(6000)
        except Exception:
            continue
        if re.search(r"令号[：:]\s*CA-OP-NS-0*"+str(int(num))+r"(?!\d)", head):
            return True
    return False


def check_card(path, C):
    txt = pathlib.Path(path).read_text(encoding="utf-8")
    lines = txt.splitlines()
    head = head_of(txt)
    out = []  # (level, msg)
    is_down = "【口令·下派】" in lines[0] if lines else False
    is_up = "【口令·上报】" in lines[0] if lines else False
    # C1 卡头必含项
    for k in C["HEADER_REQUIRED"]:
        if k not in head:
            out.append(("AMBER", f"C1 卡头缺「{k}」"))
    # C3 令号白名单（仅下派）
    m = re.search(r"令号：(\S+)", lines[0]) if lines else None
    order = m.group(1) if m else None
    if is_down:
        if not order:
            out.append(("RED", "C3 下派卡无令号"))
        elif re.match(r"^CA-OP-NS-(\d+)", order) and not _ca_issued(re.match(r"^CA-OP-NS-(\d+)", order).group(1)):
            out.append(("AMBER", f"C6 令号「{order}」借用 CA 编号：CA 从未签发过该令号（CA 卡文件号≠令号；A01 自己下的令请用 A01- 或 MLINE- 前缀，CA 令源写在令源栏）"))
        elif not any(re.match(p, order) for p in C["ALLOWED_ORDERS"]):
            out.append(("RED", f"C3 令号「{order}」不在白名单（须为三张主线卡/复位令/CA 签发令）"))
    # C2 红灯词（豁免行单列）
    hits, ex = [], 0
    for i, ln in enumerate(lines, 1):
        for w in C["BANNED_WORDS"]:
            if w in ln:
                if any(mk in ln for mk in C["EXEMPT_MARKERS"]):
                    ex += 1
                else:
                    hits.append((i, w, ln.strip()[:70]))
                break
    if hits:
        out.append(("RED" if is_down else "AMBER", f"C2 红灯词未豁免命中 {len(hits)} 行（下派卡=RED，上报卡=AMBER）：" +
                    "；".join(f"L{i}「{w}」" for i, w, _ in hits[:6])))
    # C5 冻结项：Hetionet
    if is_down:
        kw = C["HOLD_KEYWORD"]; rel = C["HOLD_RELEASE_TOKEN"]
        hk = [i for i, ln in enumerate(lines, 1) if kw in ln and not any(mk in ln for mk in C["EXEMPT_MARKERS"])
              and not re.search(r"HOLD|不许|不覆盖|不判|禁止", ln)]   # 2026-11-23：「继续HOLD／不许触碰」这类禁令句是词面假阳性，不算涉及
        if hk and rel not in txt:
            out.append(("RED", f"C5 下派卡涉及「{kw}」（L{hk[0]} 等 {len(hk)} 行）而未引 CA 重裁令 {rel}：违 HOLD-HETIONET"))
    # C7 卡头时间不得晚于章时间（卡头须写落盘时刻）
    mh = re.search(r"(\d{4})-(\d{2})-(\d{2}) (\d{2}):(\d{2}) \+0800", lines[0]) if lines else None
    ms = re.search(r"STAMP=(\d{8})T(\d{4})", txt)
    if mh and ms:
        hdr = "".join(mh.groups()); stp = ms.group(1) + ms.group(2)
        if hdr > stp:
            out.append(("AMBER", f"C7 卡头时间 {mh.group(0)} 晚于章时间 {ms.group(1)}T{ms.group(2)}：卡头须写实际落盘时刻（用 date 现读，不预估）"))
    # C4 sha16 对账：同一行里恰一个反引号路径 + 一个 16 位十六进制
    mism, nf, okc = [], [], 0
    for i, ln in enumerate(lines, 1):
        paths = re.findall(r"`([^`\s]+\.[A-Za-z0-9]+)`", ln)
        hexs = re.findall(r"(?<![0-9a-f])([0-9a-f]{16})(?![0-9a-f])", ln)
        if len(paths) == 1 and len(hexs) == 1:
            p = ROOT / paths[0]
            if p.is_file():
                if sha16(p) == hexs[0]:
                    okc += 1
                else:
                    tag = "（行内含历史/前值字样）" if re.search(r"历史|前值|改前|before", ln) else ""
                    mism.append(f"L{i} {paths[0]} 现值{sha16(p)}≠{hexs[0]}{tag}")
            else:
                nf.append(f"L{i} {paths[0]}")
    if mism:
        out.append(("AMBER", "C4 sha16 不符：" + "；".join(mism[:5])))
    info = f"C4 sha 对账：符 {okc}／不符 {len(mism)}／不在仓内 {len(nf)}（不在仓内=[待验证]）；C2 豁免行 {ex}"
    return order, is_down, is_up, out, info


def level(out):
    return 2 if any(l == "RED" for l, _ in out) else (1 if any(l == "AMBER" for l, _ in out) else 0)


NAME = {0: "GREEN", 1: "AMBER", 2: "RED"}


def cmd_card(a):
    C = cfg()
    order, down, up, out, info = check_card(a.card, C)
    lv = level(out)
    print(f"缰绳｜卡={a.card}｜类型={'下派' if down else '上报' if up else '其他'}｜令号={order}")
    for l, m in out:
        print(f"  [{l}] {m}")
    print("  [INFO]", info)
    print(f"REIN={NAME[lv]}")
    return lv


def git_ts(rel):
    r = subprocess.run(["git", "-C", str(ROOT), "log", "-1", "--format=%cI", "--", rel], capture_output=True, text=True)
    return r.stdout.strip()


def cmd_sweep(a):
    C = cfg()
    since = a.since
    if not since:
        since = git_ts("00_governance/_board/CA_首席顾问/CA_HANDOFF.md")
    print(f"缰绳 sweep｜自 {since} 起，A01 在 _board 新增/改动的卡")
    board = ROOT / "00_governance/_board"
    worst = 0; n = 0
    for p in sorted(board.glob("A01_to_*.md")):
        rel = str(p.relative_to(ROOT))
        ts = git_ts(rel)
        if not ts or ts <= since:
            continue
        n += 1
        order, down, up, out, info = check_card(p, C)
        lv = level(out); worst = max(worst, lv)
        print(f"- [{NAME[lv]}] {p.name}｜{ts[:16]}｜{'下派' if down else '上报' if up else '其他'}｜令号={order}")
        for l, m in out:
            print(f"    · [{l}] {m}")
    print(f"共 {n} 张新卡")
    if MLOG.is_file():
        rows = [r.split("\t") for r in MLOG.read_text(encoding="utf-8").splitlines()[1:]]
        recent = [r for r in rows if len(r) >= 5 and r[1] > since[:19]]
        print(f"章台账 MLINE_LOG 自该时点新增 {len(recent)} 行（A01 自盖章，仅供对照卡数）")
    print(f"REIN_SWEEP={NAME[worst]}")
    return worst


def cmd_open(a):
    now = datetime.now(TZ)
    print(f"缰绳 open｜现在 {now.isoformat(timespec='seconds')}")
    rows = [l.split("\t") for l in OPEN.read_text(encoding="utf-8").splitlines()[1:] if l.strip()]
    for r in rows:
        r += [""] * (6 - len(r))
        id_, due, owner, chk, target, note = r[:6]
        d = datetime.fromisoformat(due)
        late = now > d
        done = ""
        if chk == "file_exists" and target:
            done = "已交" if (ROOT / target).is_file() else "未交"
        state = ("逾期" if late else "未到期") + (f"｜{done}" if done else "｜人工核")
        if late and done == "已交":
            state = "已交"
        print(f"- {id_}｜{owner}｜{due[:16]}｜{state}｜{note}")
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--card"); ap.add_argument("--sweep", action="store_true")
    ap.add_argument("--since"); ap.add_argument("--open", action="store_true")
    a = ap.parse_args()
    if a.card:
        sys.exit(cmd_card(a))
    elif a.sweep:
        sys.exit(cmd_sweep(a))
    elif a.open:
        sys.exit(cmd_open(a))
    else:
        ap.print_help(); sys.exit(1)
