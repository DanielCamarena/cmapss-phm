# LaTeX package for Overleaf

This folder contains a full LaTeX version of the CMAPSS-PHM academic paper.

## Files
- `main.tex`: complete manuscript with sections, figures, and tables.
- `references.bib`: bibliography entries.

## How to use in Overleaf
1. Upload `main.tex` and `references.bib`.
2. Upload the required dashboard images from `fig/dashboard/`:
   - `dashboard_v1_4.png`
   - `dashboard_v1_5.png`
   - `dashboard_v1_8.png`
   - `dashboard_v1_9.png`
3. Compile with `pdfLaTeX` + `BibTeX`.

## Notes
- Figures F1, F2, F7, and F8 are generated natively in LaTeX with TikZ/PGFPlots.
- Tables T1--T9 are included directly in `main.tex` using project artifacts.