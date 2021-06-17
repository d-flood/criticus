# Tendon v 0.2
This is a collection of computer tools for aiding the text critical workflow from transcription to collation to analysis.
Some of the tools already exist as CLI's that I have made, but here are are collected into one place and converted to user-friendly GUI applications.

## The Problem I'm trying to Solve
The standard tool for transcribing ancient New Testament manuscripts ([ITSEE's OTE](https://itsee-wce.birmingham.ac.uk/ote/transcriptiontool)) produces files in an entirely different format from that required by the standard tool for collating these transcriptions ([the WCE Collation Editor](https://github.com/itsee-birmingham/standalone_collation_editor)).

Moving from transcription to collation to analysis requires several steps of intermediate conversion of the data along the way. Tendon is a collection of tools to help 'connect' these three basic tasks.

## What Tendon Does
Tendon is a desktop app with six tools:
1. Convert a plain text transcription of a chapter or other unit into single-verse JSON files properly formatted for use in the Collation Editor. This is the simplest way to get data into the Collation Editor.
2. Convert a repurposed superset of Markdown to TEI XML. Included is a graphical user interface (GUI) to my CLI [MarkdownTEI](https://github.com/d-flood/MarkdownTEI). This is presented as simple and offline alternative to the [Online Transcription Editor (OTE)](https://itsee-wce.birmingham.ac.uk/ote/transcriptiontool). MarkdownTEI converted files can even be uploaded to the OTE.
3. Convert TEI transcriptions (from MarkdownTEI or the OTE) to single-verse JSON files for use in the Collation Editor. This is a GUI version of my [TEI to JSON](https://github.com/d-flood/TEI-to-JSON) CLI.
4. Combine any number of single-verse collation files produced by the Collation Editor.
5. Reformat the collation file output of the Collation Editor for use with the [open-cbgm](https://github.com/jjmccollum/open-cbgm-standalone) and with Apparatus Explorer (a [desktop](https://github.com/d-flood/apparatus-explorer) and [web app](https://davidaflood.com/appex/demo/)) for visualization and editing.
6. Provide a simple way to view TEI XML transcriptions offline using the same styling as the [IGNTP online transcriptions](http://www.itseeweb.bham.ac.uk/epistulae/XML/igntp.xml).

## Installation
### Windows standalone version
Download and install the MSI from this repository.

### MacOS standalone version
*Experimental*: Download the ***unsigned*** DMG [here](https://daf-staticfiles.s3.amazonaws.com/distributables/Tendon-0.2.dmg)

### Run on any platform with Python 3.6+
Dependencies
- `lxml`
- `natsort`
- `PySide2`
- `PySimpleGUIQt`
- `Markdown==3.2.2`
- `markdown-del-ins`

With the dependencies installed, go to `<root>/src/` and call `python -m tendon`

## Brief Tutorial
Please [contact](https://www.davidaflood.com/contact/), message me on Twitter, or fill out a GitHub issue for help using these tools and to report bugs. There are certain to be untested edge cases especially when converting TEI to JSON.

![screenshot of tendon's main window](images/tendon_main_window.png)

### Plain Text to JSON Files
![screenshot of plain text to json window](images/plain_text_to_json_window.png)
The structure of the plain text (.txt) file is important. Tendon assumes:
- One verse (or other unit) per line
- Each line begins with the verse number
- There is no more than one whole chapter (or other complete unit) per file

1. Choose whether to convert all verses in a text file or to convert a range of verses (can be one verse, e.g. '3 to 3').
   - If "Range of verses" is selected, than a first ('from') and last ('to') verse must be entered. These input values must match verse numbers in the file, e.g. '7 to 12' *not* '1:7 to 1:12'.
   - If "All verses in file" is selected, then every verse will be converted to a different JSON file.
2. Choose whether to provide Tendon with the witness siglum or to have Tendon try and get this information from the input text file name.
   - If "Manual" is selected, then Tendon will use the user provided siglum and unit prefix.
     - The siglum is an identifier for the witness, e.g. 'P52'
     - The unit prefix is whatever needs to be added to the verse number to make it a full reference. This is normally the book and chapter (*with no spaces*), e.g. "Rom14", "Rom_14", "R14", "B06K14V". With this information, Tendon can create the correct directories and filenames for every verse to be converted.
   - If "Auto from file name" is selected, then Tendon will get the siglum and unit prefix from the file name *if the following convention is observed:* `<siglum>_<unit prefix>.txt`. That is, the filename should consist of the siglum, followed by an underscore, followed by the book and chapter. E.g., `P46_Rom14.txt`.
3. Choose the output directory by clicking "Browse" and navigating to the right folder.
   - If you have downloaded the Collation Editor, go to that folder and to `/collation/data/textrepo/json/`. This is where the Collation Editor expects the transcription files to be.
4. Finally, click "Convert File".
   - You will be prompted to select a plain text file.
   - Upon selecting it Tendon will attempt to convert the specified verses from the file and save them into the chosen output directory.
   - Tendon creates a folder in the output directory named after the siglum and then deposits the converted verses from that witness into the folder.
   - Tendon also creates and places a `metadata.json` file that must exist for the Collation Editor to work.
5. Caution. If you have many plain text transcription files in the same folder, and all adhere to the naming convention required by "auto from file name", then all chapter files can be converted at once by clicking "Convert Directory". 
   - This can easily result in the creation of hundreds or thousands of JSON files (which may be what you want!). So, make sure to test one of the files to ensure that its format is compatible and that the result is satisfactory before converting an entire folder.

### MarkdownTEI
This tool began as a [CLI](https://github.com/d-flood/MarkdownTEI) but here it is much more user-friendly as a GUI.
![MarkdownTEI tool screenshot of window](images/markdown_to_tei_window.png)
1. Choose how Tendon should format the converted transcription file. All options can be read by a computer but they differ most in human-readability.
   - "Do not add extra whitespace"
    ![example of no added whitespace](images/markdown_to_tei/no_extra_whitespace.png)
   - "Keep transcription lines"
    ![example of lines kept together](images/markdown_to_tei/keep_lines_example.png)
   - "Pretty Print"
    ![example of pretty printed xml](images/markdown_to_tei/pretty_print.png)
2. Select the Markdown (.md) file to be converted by clicking "Browse".
   - You will then be prompted to choose the converted file's location and name.

### TEI to JSON
This is the most difficult task. The TEI XML produced by the WYSIWYG OTE is very flexible and it is difficult to predict all of the possible combinations and nested encodings. Please tell me about bugs and edge cases.
![screenshot of TEI to JSON window](images/tei_to_json_window.png)
1. Select the TEI transcription file to be converted.
   - This can be the output of MarkdownTEI (most reliable) or the OTE.
2. Choose whether to convert all of the TEI transcription file or one verse.
   - Converting one verse is useful for correcting errors discovered in transcriptions during the collation process.
   - When working with TEI transcriptions, the verse reference format follows the IGNTP/INTF style, e.g. "B06K13V1" (B06 = Romans, K13 = chapter 13, V1 = verse 1).
3. Select the output folder where chapter folders and verse files are created and saved.
   - This should be located by going to the root folder of the Collation Editor and navigating to `/collation/data/textrepo/json/`.
4. Then click "Convert".

### Combine Collation Files
I've found that the Collation Editor fails to process more than a dozen verses at one time and it is best used one verse at a time. For analysis, these individual verse collation files should be combined into chapter and book length files.
![screenshot of Combine Collation Files window](images/combine_xml_collation_files_window.png)
1. Navigate to the folder that contains all of the files you want to combine by clicking "Browse".
2. Enter a bit of text to filter all files to be combined.
   - E.g., entering "Rom13" would combine "Rom13.1.xml" and "Rom13.2.xml" but not "Rom14.1.xml" while entering "Rom" would result in combining them all.
3. Click "Combine XML Files". You will then be prompted to select the name and location of the combined file.

### Reformat Collation File
The output of the Collation Editor has several redundancies and lacks some useful features that are needed for the file to be used as input for the open-cbgm or the Apparatus Explorer.
![screenshot of Reformat Collation File window](images/reformat_collation_file_window.png)
1. Select an XML collation file that was combined during the previous step by clicking "Browse".
2. Click "Convert". You will then be prompted to save the reformatted file.

### View TEI Transcriptions
This is a simple way to view TEI transcriptions with the same styling applied to equivalent TEI transcriptions by the IGNTP.
![screenshot of View TEI Transcriptions window](images/tei_viewer_window.png)
1. Select a folder that has one or more TEI transcriptions in it. TEI transcriptions created with MarkdownTEI will work automatically, while others will need to have the style linking element inserted.
2. Click "Launch TEI Transcription Viewer".
   - For MacOS users, ensure that Firefox is installed since this stylesheet was created by ITSEE and the IGNTP for Firefox.
   - Launching the viewer starts a local server and launches Firefox on MacOS and the default browser on Windows.
    ![screenshot of browser viewing a directory](images/tei_viewer/firefox_tei_dir.png)
   - Click on a TEI transcription to view it fully formatted and styled.
    ![screenshot of browser viewing TEI transcription with stylesheet linked](images/tei_viewer/transcription_visualization_example.png)


###### I structured and generated the standalone desktop apps with [Beeware's Briefcase](https://github.com/beeware/briefcase).