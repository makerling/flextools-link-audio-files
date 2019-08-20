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
from FTModuleClass import *
from SIL.FieldWorks.FDO import ITextFactory, IStTextFactory
from SIL.FieldWorks.Common.COMInterfaces import ITsString
import codecs

#----------------------------------------------------------------
# Documentation that the user sees:

docs = {FTM_Name        : "Insert_Audio_Pronunciation_Files_to_Lexeme_form_final",
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
    FOLDER = r'C:\ProgramData\SIL\FieldWorks\Projects\turkishaudiotest\LinkedFiles\AudioVisual'

    #------ check existence of FOLDER variable ------#
    if FOLDER == '': report.Info(u"Location of Audio files has not been set. Please add folder location path to FOLDER variable in script. Exiting...")
    report.Blank()    
    if FOLDER != '':
        report.Info(u"Folder containing audio files is: %s" % FOLDER)
    
        #------ create python lists to map audio and non-audio files in FOLDER ------#
        wavAudioFiles = []
        nonWavAudioFiles = []
        for root, dirs, file in os.walk(FOLDER):
            for audioFilename in file:
                bareAudioFilename, extension = os.path.splitext(audioFilename)
                if extension == '.wav':                 
                    wavAudioFiles.append(bareAudioFilename)
                else:
                    nonWavAudioFiles.append(audioFilename)
                    report.Info(u"following files are not valid files for attaching to lexeme form as audio files, please convert to .wav and try again: %s" % 
                        audioFilename)        
        report.Info(u"Found {0} .wav audio files in folder".format(len(wavAudioFiles)))
        
        #------ check existence of Audio writing System ------#
        vernWS = DB.GetAllVernacularWSs()
        audioWSCheck = [s for s in vernWS if "audio" in s]
        audioWS = "".join(audioWSCheck)
        report.Info(u"Audio Writing system tag is: %s" % audioWS) 
        report.Blank()
        if len(audioWSCheck) == 0: report.Info(u"Audio writing system not found, please create one for the %s default vernacular writing system. Exiting..." 
            % audioWSCheck)
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
                    audioHandle = DB.WSHandle(audioWS)     
                    audioFilename = filename + ".wav"    
                    lexEntryValue = ITsString(lexEntry.LexemeFormOA.Form.get_String(audioHandle)).Text                    
                    if lexEntryValue is not None or lexEntryValue != audioFilename or lexEntryValue == audioFilename:
                        report.Info(u"%s audio file is already linked to %s headword, skipping..." % (lexEntryValue,filename))
                    else:                        
                        #------ setting/attaching audiofilename to entry ------#
                        lexForm = lexEntry.LexemeFormOA                                            
                        mkstr = DB.db.TsStrFactory.MakeString(audioFilename, audioHandle) 
                        lexForm.Form.set_String(audioHandle, mkstr)                        
                        report.Info(u"attached %s audio file to this headword: %s" % (audioFilename,filename))
    report.Blank()        

#----------------------------------------------------------------
# The name 'FlexToolsModule' must be defined like this:

FlexToolsModule = FlexToolsModuleClass(runFunction = MainFunction,
                                       docs = docs)
            
#----------------------------------------------------------------
if __name__ == '__main__':
    FlexToolsModule.Help()
    
