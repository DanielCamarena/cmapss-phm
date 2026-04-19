from PIL import Image, ImageDraw, ImageFont
import math

W, H = 1900, 1320
bg = (245, 246, 248)
img = Image.new("RGB", (W, H), bg)
draw = ImageDraw.Draw(img)

def get_font(size, bold=False):
    paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
    ]
    for p in paths:
        try:
            return ImageFont.truetype(p, size)
        except:
            pass
    return ImageFont.load_default()

font_title = get_font(42, True)
font_sub = get_font(24, True)
font_phase = get_font(18, True)
font_head = get_font(24, True)
font_card_head = get_font(20, True)
font_body = get_font(18, False)
font_formula = get_font(17, False)

# Proposed reordered palette:
# Problem = terracotta, Data = steel blue, Modeling = deep teal,
# System = plum, Evaluation = amber, Insights = dark red
titleblue = "#17335C"
accent = "#C78A2D"

problem_col = "#B5653A"   # terracotta
data_col = "#4D6C8A"      # steel blue
model_col = "#2A6F6B"     # deep teal
system_col = "#6D597A"    # plum
eval_col = "#A47600"      # amber
ins_col = "#9C3D54"       # dark rose/red

fills = {
    problem_col: "#FCF1EA",
    data_col: "#EEF3F8",
    model_col: "#ECF7F5",
    system_col: "#F3EEF7",
    eval_col: "#FFF8EA",
    ins_col: "#FAEEF1",
}

def rounded_box(x1, y1, x2, y2, radius, fill, outline, width=3):
    draw.rounded_rectangle((x1, y1, x2, y2), radius=radius, fill=fill, outline=outline, width=width)

def draw_centered_wrapped(xc, yc, text, font, fill, max_width, line_spacing=4):
    lines = []
    for para in text.split("\n"):
        words = para.split()
        if not words:
            lines.append("")
            continue
        line = words[0]
        for w in words[1:]:
            cand = f"{line} {w}"
            if draw.textlength(cand, font=font) <= max_width:
                line = cand
            else:
                lines.append(line)
                line = w
        lines.append(line)
    txt = "\n".join(lines)
    bbox = draw.multiline_textbbox((0, 0), txt, font=font, spacing=line_spacing, align="center")
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.multiline_text((xc - tw / 2, yc - th / 2), txt, font=font, fill=fill, spacing=line_spacing, align="center")

def arrow(x1, y1, x2, y2, color="#6A6A6A", width=6, head=18):
    draw.line((x1, y1, x2, y2), fill=color, width=width)
    ang = math.atan2(y2 - y1, x2 - x1)
    a1 = ang + math.pi * 0.86
    a2 = ang - math.pi * 0.86
    p1 = (x2 + head * math.cos(a1), y2 + head * math.sin(a1))
    p2 = (x2 + head * math.cos(a2), y2 + head * math.sin(a2))
    draw.polygon([(x2, y2), p1, p2], fill=color)

# Banner
draw.rectangle((0, 0, W, 92), fill=titleblue)
draw.rectangle((0, 92, W, 100), fill=accent)
draw_centered_wrapped(W / 2, 46, "PROJECT RESEARCH ROADMAP", font_title, "white", W - 80)
draw_centered_wrapped(W / 2, 142, "PHM System for NASA C-MAPSS", font_sub, titleblue, W - 80)
draw_centered_wrapped(W / 2, 178, "Benchmark prediction → deployable decision support", font_sub, titleblue, W - 120)

panel_w, panel_h = 415, 500
gap_x = 105
left = 48
top_y = 240
bot_y = 760
xs = [left + i * (panel_w + gap_x) for i in range(3)]

def draw_phase_panel(x, y, phase_no, title, color, boxes, emphasize=False):
    fill = fills[color]
    rounded_box(x, y, x + panel_w, y + panel_h, 14, fill, color, 3)
    draw.rectangle((x, y, x + panel_w, y + 88), fill=color)
    draw_centered_wrapped(x + panel_w / 2, y + 18, f"PHASE {phase_no:02d}", font_phase, "#F4D86B", panel_w - 30)
    draw_centered_wrapped(x + panel_w / 2, y + 56, title, font_head, "white", panel_w - 34, line_spacing=2)
    if emphasize:
        rounded_box(x - 10, y - 10, x + panel_w + 10, y + panel_h + 10, 18, None, color, 4)

    inner_x = x + 28
    inner_w = panel_w - 56
    cur_y = y + 114
    gap = 16

    for kind, header, body in boxes:
        bh = 72 if kind == "small" else 98
        font_b = font_formula if kind == "small" else font_body
        rounded_box(inner_x, cur_y, inner_x + inner_w, cur_y + bh, 10, "white", color if kind != "alt" else accent, 2)
        draw_centered_wrapped(inner_x + inner_w / 2, cur_y + 18, header, font_card_head, "#111111", inner_w - 26, line_spacing=2)
        draw_centered_wrapped(inner_x + inner_w / 2, cur_y + bh / 2 + 12, body, font_b, "#111111", inner_w - 34, line_spacing=3)
        cur_y += bh + gap

phase1 = [
    ("normal", "Research Gap", "Benchmark RUL models stop at prediction"),
    ("normal", "Objective", "Build a traceable PHM system"),
    ("normal", "Scope", "NASA C-MAPSS benchmark\ndeployable workflow"),
]
phase2 = [
    ("normal", "Dataset", "FD001–FD004 trajectories\nsettings + sensor signals"),
    ("normal", "Feature Pipeline", "Low-variance filtering\nselected predictive subset"),
    ("normal", "Target & Scaling", "Training-only standardization\ncapped RUL + audit visibility"),
]
phase3 = [
    ("normal", "Candidate Models", "RF, HGB, LSTM, GRU\ntabular vs sequence"),
    ("normal", "Selection Logic", "Accuracy, latency, robustness\nserving stability"),
    ("normal", "Champion / Fallback", "RF deployed  |  HGB fallback"),
]
phase4 = [
    ("normal", "Predictive Layer", "Calibrated RUL estimate\nconfidence band + trace"),
    ("normal", "Agent Layer", "Deterministic risk engine\nrecommendation + state"),
    ("normal", "Dashboard & Contracts", "Summary / Analysis / Scenarios / Audit\ncontracts + states"),
]
phase5 = [
    ("normal", "Predictive Metrics", "RMSE / MAE across models\nglobal + per-dataset evidence"),
    ("normal", "Engineering Metrics", "Latency, fallback behavior, stability\ndeployment-oriented checks"),
    ("small", "Metric", "RMSE = √(1/n Σ(y−ŷ)²)"),
    ("normal", "Key Result", "Best benchmark model\n≠ best deployed model"),
]
phase6 = [
    ("normal", "Main Insight", "Deterministic decisions matter\nbeyond raw scores"),
    ("normal", "Traceability", "Contracts, audit records, scenarios\nmake PHM reviewable"),
    ("normal", "Contribution", "Deployable PHM system\nprediction + decision + traceability"),
]

draw_phase_panel(xs[0], top_y, 1, "Problem\nFraming", problem_col, phase1)
draw_phase_panel(xs[1], top_y, 2, "Data &\nPreprocessing", data_col, phase2)
draw_phase_panel(xs[2], top_y, 3, "Modeling", model_col, phase3)

draw_phase_panel(xs[0], bot_y, 4, "System\nArchitecture", system_col, phase4)
draw_phase_panel(xs[1], bot_y, 5, "Evaluation &\nEvidence", eval_col, phase5)
draw_phase_panel(xs[2], bot_y, 6, "Insights &\nContribution", ins_col, phase6, emphasize=True)

# Connectors
mid_y_top = top_y + 250
arrow(xs[0] + panel_w, mid_y_top, xs[1], mid_y_top, color=accent, width=6, head=18)
arrow(xs[1] + panel_w, mid_y_top, xs[2], mid_y_top, color=accent, width=6, head=18)

x_start = xs[2] + panel_w / 2
y_start = top_y + panel_h
channel_y = 708
x_end = xs[0] + panel_w / 2
y_end = bot_y
draw.line((x_start, y_start, x_start, channel_y), fill="#6A6A6A", width=6)
draw.line((x_start, channel_y, x_end, channel_y), fill="#6A6A6A", width=6)
arrow(x_end, channel_y, x_end, y_end, color="#6A6A6A", width=6, head=18)

mid_y_bot = bot_y + 250
arrow(xs[0] + panel_w, mid_y_bot, xs[1], mid_y_bot, color=accent, width=6, head=18)
arrow(xs[1] + panel_w, mid_y_bot, xs[2], mid_y_bot, color=accent, width=6, head=18)

out = "/mnt/data/phm_research_roadmap_reordered_colors.png"
img.save(out)
print(out)