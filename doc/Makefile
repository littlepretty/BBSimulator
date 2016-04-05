PDFLATEX=pdflatex
LATEX=latex
BIBTEX=bibtex
DVI2PDF=dvipdf
PS2PDF=ps2pdf
UNAME:=$(shell uname -s)
ifeq ($(UNAME),Linux)
	VIEWER=xdg-open
endif
ifeq ($(UNAME), Darwin)
	VIEWER=open
endif

FILE_NAME=bbscheduler
PDFLATEX_OPT=-file-line-error-style -interaction=nonstopmode

.PHONY: all, clean, view

all:
	$(PDFLATEX) $({PDFLATEX_OPT) $(FILE_NAME).tex
	$(BIBTEX) $(FILE_NAME).aux
	$(PDFLATEX) $({PDFLATEX_OPT) $(FILE_NAME).tex
	$(PDFLATEX) $({PDFLATEX_OPT) $(FILE_NAME).tex

view: all
	$(VIEWER) $(FILE_NAME).pdf
	rm *.log *.aux *.blg *.bbl

clean:
	rm *.log *.aux *.dvi *.out *.blg *.bbl *.ps *.bak
