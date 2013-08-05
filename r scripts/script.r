library(ggplot2)
library(plyr)
library(scales)


# Load data generated by ../analyticstestingtwo.py
playlistContents <- read.table('../playlists.txt', sep=',', header=T)
titles <- read.table('../videoIdsAndTitles.txt', sep=',')
colnames(titles) <- c('videoId', 'videoTitle')
viewsOfVideoOne <- read.table('../datesAndViews.txt', sep=',')
viewsOfVideoTwo <- read.table('../2013-04-14datesAndViews.txt', sep=',')
viewsOfVideoCombined <- rbind(viewsOfVideoOne, viewsOfVideoTwo)
viewsOfVideo <- viewsOfVideoCombined[!duplicated(viewsOfVideoCombined), ]
colnames(viewsOfVideo) <- c('videoId', 'date', 'views')
viewsOfVideo$date <- as.Date(viewsOfVideo$date)

viewOnPlaylists <- merge(viewsOfVideo, playlistContents, by='videoId')

# Calculate total number of views
totalViewsPerDate <- ddply(viewOnPlaylists, .(date, playlistTitle), summarize, totalViews=sum(views))

# General overview of minutes watched on different playlists.
p <- ggplot(totalViewsPerDate) + 
    geom_line(aes(date, totalViews, colour=playlistTitle)) + 
    xlab('Dato') + ylab('Minutter set')
#p
ggsave("plots/01 General overview.pdf", p, width=10, height=6)

# Specific view of fall semester and IFG1 videos
inFallSemester = subset(totalViewsPerDate, 
                        as.Date(totalViewsPerDate$date) > "2012-09-01" &
                          as.Date(totalViewsPerDate$date) < "2013-01-31")
p <- ggplot(subset(inFallSemester, inFallSemester$playlistTitle == 'IFG1 - Introduktion til Matematik og Fysik')) + 
  geom_line(aes(date, totalViews)) + 
  xlab('Dato') + ylab('Minutter set')
#p
ggsave("plots/02 Minutes watched of IFG1 in fall semester 2013.pdf", p)



cumulatedViewsPerDate = ddply(totalViewsPerDate, .(playlistTitle), transform, viewsCumulated = cumsum(totalViews))
p <- ggplot(cumulatedViewsPerDate) + 
  geom_line(aes(date, viewsCumulated, colour=playlistTitle)) + 
  xlab('Dato') + ylab('Tid [min]') + 
  opts(title = 'Samlet antal sete videominutter', legend.position=c(0.2,0.8))
#p
ggsave("plots/03 Cumulated minutes of watched video.pdf", p, width=10, height=6)

p <- ggplot(cumulatedViewsPerDate) + 
  geom_line(aes(date, viewsCumulated, colour=playlistTitle), alpha=0.5) + 
  geom_line(data=totalViewsPerDate, aes(date, 4*totalViews, colour=playlistTitle), alpha=1.0) + 
  xlab('Dato') + ylab('Samlet set tid [min] eller 4 x tid set per dag [min]') + 
  scale_x_date(breaks = "1 month", minor_breaks = "1 week", labels=date_format("%d %b %Y")) +
  opts(title = 'Samlet antal sete videominutter', legend.position=c(0.2,0.8)) + 
  scale_colour_discrete(name = "Playlist")
p
ggsave("plots/04 Cumulated minutes of watched video.pdf", p, width=10, height=6)

