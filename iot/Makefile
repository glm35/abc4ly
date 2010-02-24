SHELL=/bin/bash
# Note: by default, GNU Make uses /bin/sh which is /bin/dash on Debian
# systems, which causes some surprises with the commands. For instance,
# stdout+stderr IO redirection with "&>" does not work with dash.

#LILY_PREFIX=/usr/local/bin
#LILYPOND=${LILY_PREFIX}/lilypond
#ABC2LY=${LILY_PREFIX}/abc2ly
LILYPOND=lilypond
ABC2LY=${HOME}/Documents/code/abc4ly/abc4ly.py

src=${HOME}/Musique/tunebook/tunes
#src2=${HOME}/Musique/tunebook/tunes/broken

ly_outdir=ly-out

lyfiles := $(patsubst ${src}/%.abc,${ly_outdir}/%.ly,$(wildcard ${src}/*.abc))
#lyfiles2 := $(patsubst ${src2}/%.abc,${ly_outdir}/%.ly,$(wildcard ${src2}/*.abc))

pdffiles := $(patsubst ${src}/%.abc,${ly_outdir}/%.pdf,$(wildcard ${src}/*.abc))
#pdffiles2 := $(patsubst ${src2}/%.abc,${ly_outdir}/%.pdf,$(wildcard ${src2}/*.abc))

all : ${ly_outdir} ${lyfiles} ${lyfiles2}

pdf : ${ly_outdir} ${pdffiles} ${pdffiles2}

${ly_outdir}/%.pdf : ${ly_outdir}/%.ly
	@echo [LILYPOND] $<
	@${LILYPOND} -o ${ly_outdir}/$* $<

${ly_outdir}/%.ly : ${src}/%.abc ${ABC2LY}
	@echo [ABC2LY] $<
	@${ABC2LY} -o $@ $<

#${ly_outdir}/%.ly : ${src2}/%.abc ${ABC2LY}
#	@echo [ABC2LY] $<
#	@${ABC2LY} -o $@ $<

${ly_outdir} :
	@echo [MKDIR] ${ly_outdir}
	@mkdir ${ly_outdir}

stats: ${ly_outdir}
	@echo -n "Number of ABC files: "
	@find ${src} -name "*.abc" |wc -l
	@echo -n "Number of generated ly files: "
	@find ${ly_outdir} -name "*.ly" |wc -l
	@echo -n "Number of compiled ly files: "
	@find ${ly_outdir} -name "*.pdf" |wc -l

clean :
	@echo [CLEANING]
	@-rm -rf ${ly_outdir}
	@-rm -f *~

help:
	@echo "Targets:"
	@echo "        default: run ${ABC2LY} on all .abc files"
	@echo "        clean: remove all the generated files"
