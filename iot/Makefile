SHELL=/bin/bash
# Note: by default, GNU Make uses /bin/sh which is /bin/dash on Debian
# systems, which causes some surprises with the commands. For instance,
# stdout+stderr IO redirection with "&>" does not work with dash.

LILY_PREFIX=/usr/local/bin
LILYPOND_BOOK=${LILY_PREFIX}/lilypond-book
ABC2LY=${LILY_PREFIX}/abc2ly
CONVERT_LY=${LILY_PREFIX}/convert-ly

src=../../tunebook/tunes
ly_outdir=ly-out

lyfiles := $(patsubst ${src}/%.abc,${ly_outdir}/%.ly,$(wildcard ${src}/*.abc))

all : ${ly_outdir} ${lyfiles}

${ly_outdir}/%.ly : ${src}/%.abc
	@echo [ABC2LY] $<
	${ABC2LY} -o $@ $<
#	@${ABC2LY} -o $@ $< 2>${ly_outdir}/abc2ly.log
#	@cat ${ly_outdir}/abc2ly.log |grep Warning |grep -v "Q specification" || true
# Note:
# - split into two commands to be able to filter abc2ly output without losing
# the return code
# - we don't care about grep return code

${ly_outdir} :
	@echo [MKDIR] ${ly_outdir}
	@mkdir ${ly_outdir}

clean :
	@echo [CLEANING]
	@-rm -rf ${ly_outdir}
	@-rm -f *~

help:
	@echo "Targets:"
	@echo "        default: run ${ABC2LY} on all .abc files"
	@echo "        clean: remove all the generated files"
