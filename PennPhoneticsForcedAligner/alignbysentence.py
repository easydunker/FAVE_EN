#!/bin/sh
# encoding: utf-8

#  alignbysentence.py
#  
#  Created by Eleanor Chodroff on 12/30/14.
#
import os
import sys
import wave
import re
import os.path
import csv
import align
import codecs
import getopt

sr_override = 16000 #choose sampling rate: 8000, 11025, 16000
# at beginning of align.py, insert line: sr_models = None
surround_token = "sp"
between_token = "sp"
HOMEDIR = '.'
MODEL_DIR = HOMEDIR + '/model'


def getopt2(name, opts, default=None):
    value = [v for n, v in opts if n == name]
    if len(value) == 0:
        return default
    return value[0]

def getPinyin(wrds):
    tmpbase = '/tmp/' + os.environ['USER'] + '_' + str(os.getpid())
    pinyinf = codecs.open(tmpbase + "-pinyin.txt", 'w', 'utf-8')
    print wrds
    pinyinf.write(wrds)
    pinyinf.close()
    cmd = "adso -y -f " + tmpbase + "-pinyin.txt" + "|sed 's/[1-9]/& /g' >" + tmpbase + "-pinyin.out"
    ok = os.system(cmd)
    os.system("rm -f " + tmpbase + "-pinyin.txt")
    if ok != 0:
        print "Ignoring line as adso generates bad character with words: " + wrds
        return None

    tmpf = open(tmpbase + "-pinyin.out")
    pinyin = tmpf.readline()
    os.system("rm -f " + tmpbase + "-pinyin.out")
    return pinyin


def writeTextGridWithCn(outfile, phons, words, chars):

    # write the phone interval tier
    fw = codecs.open(outfile, 'w', 'utf-8')
    fw.write('File type = "ooTextFile short"\n')
    fw.write('"TextGrid"\n')
    fw.write('\n')
    fw.write(str(phons[0][1]) + '\n')
    fw.write(str(phons[-1][2]) + '\n')
    fw.write('<exists>\n')
    fw.write('3\n')


    fw.write('"IntervalTier"\n')
    fw.write('"phone"\n')
    fw.write(str(phons[0][1]) + '\n')
    fw.write(str(phons[-1][-1]) + '\n')
    fw.write(str(len(phons)) + '\n')
    for k in range(len(phons)):
        fw.write(str(phons[k][1]) + '\n')
        fw.write(str(phons[k][2]) + '\n')
        fw.write('"' + phons[k][0] + '"' + '\n')

    # write the word interval tier
    fw.write('"IntervalTier"\n')
    fw.write('"word"\n')
    fw.write(str(phons[0][1]) + '\n')
    fw.write(str(phons[-1][-1]) + '\n')
    fw.write(str(len(words)) + '\n')
    for k in range(len(words)):
        fw.write(str(words[k][1]) + '\n')
        fw.write(str(words[k][2]) + '\n')
        fw.write('"' + words[k][0] + '"' + '\n')

    fw.write('"IntervalTier"\n')
    fw.write('"cn"\n')
    fw.write(str(phons[0][1]) + '\n')
    fw.write(str(phons[-1][-1]) + '\n')
    fw.write(str(len(chars)) + '\n')
    for k in range(len(chars)):
        fw.write(str(chars[k][1]) + '\n')
        fw.write(str(chars[k][2]) + '\n')
        fw.write('"' + chars[k][0] + '"' + '\n')

    fw.close()

def constructResult(word_alignments, chars):
    # make the list of just phone alignments
    phons = []
    for wrd in word_alignments:
        if len(wrd) == 1:
            continue
        phons.extend(wrd[1:])  # skip the word label

    # make the list of just word alignments
    # we're getting elements of the form:
    #   ["word label", ["phone1", start, end], ["phone2", start, end], ...]
    wrds = []
    idxChars = 0
    for i in range(len(word_alignments)):
        wrd = word_alignments[i]
        # If no phones make up this word, then it was an optional word
        # like a pause that wasn't actually realized.
        if len(wrd) == 1:
            continue
        if wrd[0] == 'sp':
            wrds.append([wrd[0], wrd[1][1], wrd[-1][2], wrd[0]])  # word label, first phone start time, last phone end time
        else:
            if idxChars >= len(chars):
                print 'bad. missing Hanzi.'
                return None, None, None
            wrds.append([wrd[0], wrd[1][1], wrd[-1][2], chars[idxChars]])
            idxChars += 1

    # write the phone interval tier
    # fw = open(outfile, 'w')
    # fw.write('File type = "ooTextFile short"\n')
    # fw.write('"TextGrid"\n')
    # fw.write('\n')
    # fw.write(str(phons[0][1]) + '\n')
    # fw.write(str(phons[-1][2]) + '\n')
    # fw.write('<exists>\n')
    # fw.write('3\n')
    #
    # fw.write('"IntervalTier"\n')
    # fw.write('"phone"\n')
    # fw.write(str(phons[0][1]) + '\n')
    # fw.write(str(phons[-1][-1]) + '\n')
    # fw.write(str(len(phons)) + '\n')
    # for k in range(len(phons)):
    #     fw.write(str(phons[k][1]) + '\n')
    #     fw.write(str(phons[k][2]) + '\n')
    #     fw.write('"' + phons[k][0] + '"' + '\n')

    # write the word interval tier
    # fw.write('"IntervalTier"\n')
    # fw.write('"word"\n')
    # fw.write(str(phons[0][1]) + '\n')
    # fw.write(str(phons[-1][-1]) + '\n')
    # fw.write(str(len(wrds)) + '\n')
    # for k in range(len(wrds) - 1):
    #     fw.write(str(wrds[k][1]) + '\n')
    #     fw.write(str(wrds[k + 1][1]) + '\n')
    #     fw.write('"' + wrds[k][0] + '"' + '\n')
    #
    # fw.write(str(wrds[-1][1]) + '\n')
    # fw.write(str(phons[-1][2]) + '\n')
    # fw.write('"' + wrds[-1][0] + '"' + '\n')
    words_result = []
    chars_result = []
    for k in range(len(wrds) - 1):
        words_result.append([wrds[k][0], wrds[k][1], wrds[k+1][1]])
        chars_result.append([wrds[k][-1], wrds[k][1], wrds[k+1][1]])
    words_result.append([wrds[-1][0], wrds[-1][1], phons[-1][2]])
    chars_result.append([wrds[-1][-1], wrds[-1][1], phons[-1][2]])
    return phons, words_result, chars_result

def alignSentence(wavfile, start, end, sentence, chars, dict_alone):
    # If no model directory was said explicitly, get directory containing this script.
    hmmsubdir = "FROM-SR"

    # sr_models = [8000, 11025, 16000]
    word_dictionary = "./tmp/dict"
    input_mlf = './tmp/tmp.mlf'
    output_mlf = './tmp/aligned.mlf'
    tmptrsfile = "./tmp/tmptrs.txt"

    # create working directory
    align.prep_working_directory()

    # create ./tmp/dict by concatening our dict with a local one
    if dict_alone:
        os.system("cat " + dict_alone + " > " + word_dictionary)
    else:
        os.system("cat " + HOMEDIR + "/model/dict > " + word_dictionary)

    # prepare wavefile: do a resampling if necessary
    tmpwav = "./tmp/sound.wav"
    SR = align.prep_wav(wavfile, tmpwav, sr_override, start, end)

    if hmmsubdir == "FROM-SR":
        hmmsubdir = "/" + str(SR)

    # prepare trsfile
    with open(tmptrsfile, 'w') as fw:
        writer = csv.writer(fw)
        sentence = sentence.replace("  ", " ")
        writer.writerow(sentence)
        fw.close()
        wave_start = start
        wave_end = end

    # prepare mlfile
    align.prep_mlf(tmptrsfile, input_mlf, word_dictionary, surround_token, between_token)

    # prepare scp files
    align.prep_scp(tmpwav)

    # generate the plp file using a given configuration file for HCopy
    align.create_plp(HOMEDIR + '/model' + hmmsubdir + '/config')

    # run Verterbi decoding
    # print "Running HVite..."
    mpfile = HOMEDIR + '/model' + '/monophones'
    if not os.path.exists(mpfile):
        mpfile = HOMEDIR + '/model' + '/hmmnames'
    align.viterbi(input_mlf, word_dictionary, output_mlf, mpfile, HOMEDIR + '/model' + hmmsubdir)

    # output the alignment as a Praat TextGrid
    sentenceAlign = align.readAlignedMLF(output_mlf, SR, float(wave_start))
    return constructResult(sentenceAlign, chars)

if __name__ == '__main__':

    try:
        opts, args = getopt.getopt(sys.argv[1:], "r:d:p:")

        # get the three mandatory arguments
        wavfile, trsfile, outfile = args
        # get options
        sr_override = getopt2("-r", opts)
        dict_alone = getopt2("-d", opts)

    except:
        print __doc__
        sys.exit(0)

    alignRes = []
    all_phons = []
    all_words = []
    all_chars = []
    with codecs.open(trsfile, 'r', 'utf-8') as f:
        lines = f.readlines()
        f.close()
        for line in lines:
            columns = line.split()
            if len(columns) < 3:
                 break
            if len(columns[2].strip()) < 1:
                 continue
            sentCntmp = columns[2]
            sentCntmp = sentCntmp.replace("\"", "")
            sentCntmp = sentCntmp.replace("\n", "")
            pinyin = getPinyin(sentCntmp)
            if pinyin is None:
                continue
            sentCntmp = sentCntmp.replace("", " ")
            phons, words, chars = alignSentence(wavfile, str(columns[0]), str(columns[1]), pinyin,
                  sentCntmp.split(), dict_alone)
            if phons is not None:
                all_phons.extend(phons)
                all_words.extend(words)
                all_chars.extend(chars)

    writeTextGridWithCn(outfile, all_phons, all_words, all_chars)
    os.system("rm -r ./tmp")


