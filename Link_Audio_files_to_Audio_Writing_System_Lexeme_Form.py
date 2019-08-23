# -*- coding: utf-8 -*-
#
#   Link_Audio_files_to_Audio_Writing_System_Lexeme_Form.py
#    - A FlexTools Module -
#   See Fieldworks help topic: Audio files overview, Writing System Properties overview (how to add Audio Writing System)
#
#   Links Audio wavfiles to Audio Variant Writing System Lexeme Form in Fieldworks
#
#   stevan_vanderwerf@sil.org
#   August 2019
#
#   Platforms: Python .NET and IronPython

import os, os.path   #for os.walk method
import unicodedata

from FTModuleClass import *

from SIL.FieldWorks.FDO import ITextFactory, IStTextFactory
from SIL.FieldWorks.Common.COMInterfaces import ITsString


#----------------------------------------------------------------
# Documentation that the user sees:

docs = {FTM_Name        : "Link Audio files to Lexeme Form Audio Writing System.",
        FTM_Version     : 1,
        FTM_ModifiesDB  : True,
        FTM_Synopsis    : "Links Audio files to Lexeme Form Audio Writing System.",
        FTM_Description :
u"""
This script links existing audio files (pronunciations) to their corresponding lexeme forms in the audio variant writing systems field. 
It assumes that the audio variant writing system has already been created, if not, the script will stop and prompt you to create it. 
The files must be in .wav format and named as their corresponding headwords. You can run this script multiple times safely, 
it checks if entries already have a linked file. See Fieldworks help topics for more information about
how to create a variant audio writing system or further information about pronuncations and audio files:
Audio files overview, Writing System Properties overview (how to add Audio Writing System)
""" }
                 
#----------------------------------------------------------------
# The main processing function

def MainFunction(DB, report, modifyAllowed):

    #edit this variable with the filesystem folder location of the Audio files, keep the "r" and single quotes
    FOLDER = r''

    #------ check existence of FOLDER variable ------#
    if FOLDER == '': report.Info(u"Location of Audio files has not been set. Please add folder location path to FOLDER variable in script. Exiting...")
    report.Blank()    
    if FOLDER != '':
        report.Info(u"Folder containing audio files is: %s" % FOLDER)
    
        #------ create python lists to map audio and non-audio files in FOLDER ------#
        wavAudioFiles = []
        nonWavAudioFiles = []
        for root, dirs, files in os.walk(unicode(FOLDER)):
            for audioFilename in files:
                # FLEx stores its data as decomposed unicode, so
                # convert the filenames to match.
                audioFilename = unicodedata.normalize('NFD', 
                                                      audioFilename)
                bareAudioFilename, extension = os.path.splitext(audioFilename)
                if extension == '.wav':                 
                    wavAudioFiles.append(bareAudioFilename)
                else:
                    nonWavAudioFiles.append(audioFilename)
                    report.Info(u"This file is not a valid file for attaching to the lexeme form as an audio file. Please convert to .wav and try again: %s" % 
                        audioFilename)        
        report.Info(u"Found {0} .wav audio files in folder".format(len(wavAudioFiles)))
        
        #------ check existence of Audio writing System ------#
        vernWS = DB.GetAllVernacularWSs()
        audioWSCheck = [s for s in vernWS if "audio" in s]
        # CDF: this won't work if there is more than 1 audio WS...
        audioWS = "".join(audioWSCheck)
        audioHandle = DB.WSHandle(audioWS)     
        report.Info(u"Audio Writing system tag is: %s" % audioWS) 
        report.Blank()
        if not audioHandle: 
            report.Error(u"Audio writing system not found, please create one for the default vernacular writing system. Exiting...")
        else: 
            #------ create python dictionary to map headwords and lexForm objects ------#
            headwords = {}
            for entry in DB.LexiconAllEntries():
                headword = DB.LexiconGetHeadword(entry).rstrip()    #stripping out stray spaces at end of entry
                headwords[headword] = entry
            
            #------ checking to see if headword from audio file exists in lexicon ------#            
            for filename in wavAudioFiles:
                if filename not in headwords:
                    report.Info(u"%s headword from audio filename was not found in lexicon, skipping..." % (filename))
                else:
                    #------ checking to see if something is already set/attached to entry ------#
                    lexEntry = headwords.get(filename)  
                    audioFilename = filename + ".wav"    
                    lexEntryValue = ITsString(lexEntry.LexemeFormOA.Form.get_String(audioHandle)).Text                    
                    if lexEntryValue is not None:
                        report.Info(u"%s audio file is already linked to %s headword, skipping..." % (lexEntryValue,filename))
                    else:                        
                        #------ setting/attaching audiofilename to entry ------#
                        report.Info(u"Attaching %s audio file to headword %s" % (audioFilename,filename))
                        if modifyAllowed:
                            lexForm = lexEntry.LexemeFormOA                                            
                            mkstr = DB.db.TsStrFactory.MakeString(audioFilename, audioHandle) 
                            lexForm.Form.set_String(audioHandle, mkstr)
                        else:
                            report.Info(">>Use Run (Modify) to make the change.")
    report.Blank()        

#----------------------------------------------------------------
# The name 'FlexToolsModule' must be defined like this:

FlexToolsModule = FlexToolsModuleClass(runFunction = MainFunction,
                                       docs = docs)
            
#----------------------------------------------------------------
if __name__ == '__main__':
    FlexToolsModule.Help()
    
