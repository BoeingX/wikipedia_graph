#!/bin/bash
neo4j-import --into wikipedia-stats.db --id-type integer --delimiter TAB --nodes:Article enwiki-20080103-page-header.csv,enwiki-20080103-page-stats.csv --relationships:TO_ARTICLE enwiki-20080103-pagelinks-header.csv,enwiki-20080103-pagelinks-stats.csv 
