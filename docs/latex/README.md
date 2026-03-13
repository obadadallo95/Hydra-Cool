# LaTeX Manuscript Package

This folder contains a generic journal-style LaTeX manuscript and a BibTeX reference file for Hydra-Cool.

Files:

- `manuscript.tex`
- `references.bib`

## Build

```bash
pdflatex manuscript.tex
bibtex manuscript
pdflatex manuscript.tex
pdflatex manuscript.tex
```

The current template uses the standard `article` class so that it stays portable. If you later target a specific venue, you can replace the class with the required publisher template while keeping the body text and bibliography entries.
