# move textgrid boundaries as specified in table
dir$ = "/Users/mac232/Documents/PROJECT/Diss/Diss_Analysis/Aligner/AlignedOutput"
Create Strings as file list... list 'dir$'/*.wav
wavFileName$ = Get string... 1
wavfilename$ = wavFileName$ - ".wav"
Create Strings as file list... list 'dir$'/*.csv
Sort
nFiles = Get number of strings
Read from file... 'dir$'/'wavfilename$'.wav
select Sound 'wavfilename$'
To TextGrid... "phone word cn"
for ifile from 1 to nFiles
	select Strings list
	filename$ = Get string... 'ifile'
	basename$ = filename$ - ".csv"
	call markTextGrid 'basename$'
endfor
select TextGrid 'wavfilename$'
Write to text file... 'dir$'/'wavfilename$'.TextGrid

procedure markTextGrid basename$
	#pause 'basename$'
	#Read from file... 'dir$'/'wavfilename$'.wav
	Read Table from comma-separated file... 'dir$'/'basename$'.csv
	
	#select Sound 'wavfilename$'
	#To TextGrid... "phone word cn"
	select Table 'basename$'
	nRows = Get number of rows
	#pause
	for i from 1 to nRows
		select Table 'basename$'
		tmin = Get value... i tmin
		tier$ = Get value... i tier
		text$ = Get value... i text
		select TextGrid 'wavfilename$'
		if index_regex(tier$, "phone")
			Insert boundary... 1 tmin
			j = Get interval at time... 1 tmin+0.0001
			Set interval text... 1 j 'text$'
		elsif index_regex(tier$, "word")
			Insert boundary... 2 tmin
			j = Get interval at time... 2 tmin+0.0001
			Set interval text... 2 j 'text$'
        else 
            Insert boundary... 3 tmin
			j = Get interval at time... 3 tmin+0.0001
			Set interval text... 3 j 'text$'
		endif
	endfor
	#select TextGrid 'wavfilename$'
	#Write to text file... 'dir$'/'basename$'.TextGrid
	#select TextGrid 'wavfilename$'
	#select Sound 'wavfilename$'
	select Table 'basename$'
	Remove
endproc