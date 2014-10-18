LOGFILE := $(shell date +'%Y-%m-%d_%H:%M:%S')

getDataFromYoutube:
	ipython retrievedatafromyoutube.py
	@echo $(LOGFILE)
	@mkdir $(LOGFILE)
	@mkdir $(LOGFILE)/plots
	@cp Makefile $(LOGFILE)/Makefile
	@cp videoIdsAndTitles.txt $(LOGFILE)/
	@cp datesAndViews.txt $(LOGFILE)/
	@cp playlists.txt $(LOGFILE)/
	@cp r\ scripts/script.r $(LOGFILE)/
	@cp r\ scripts/youtubestatistics.Rnw $(LOGFILE)/
	cd $(LOGFILE) && make generatePlots

generatePlots:
	Rscript -e "library(knitr); knit('youtubestatistics.Rnw')"
	pdflatex youtubestatictics.tex
