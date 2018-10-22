#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
ZetCode PyQt4 tutorial 

In this example, we select a file with a
QtGui.QFileDialog and display its contents
in a QtGui.QTextEdit.

author: Jan Bodnar
website: zetcode.com 
last edited: October 2011
"""
import os
import re
import sys
import getpass
import shutil
import syntax
import time
import calendar
from PyQt4 import QtGui, QtCore

#=============================================================================================================
class FormWidget(QtGui.QWidget):
  def __init__(self):
    super(FormWidget, self).__init__()
    self.grid = QtGui.QGridLayout()
    self.setLayout(self.grid)
    self.initUI()

  def initUI(self):
    #Variables
    self.save_location = "/home/project.libs_3"

    #Draw Header
    self.title = QtGui.QLabel(self)
    self.title.setText("Files Under Review")
    self.title.setFont(QtGui.QFont('SansSerif', 20))
    self.grid.addWidget(self.title, 0, 0)

    self.filesUnderReview = self.getFilesUnderReview("filesUnderReview.txt")
    self.btns = []
    for idx, _file in enumerate(self.filesUnderReview):
      #Labels
      file_lbl = QtGui.QLabel(self)
      file_lbl.setText(_file[0])
      self.grid.addWidget(file_lbl, idx+1, 0)
      name_lbl = QtGui.QLabel(self)
      name_lbl.setText("(" + _file[1] + ")")
      self.grid.addWidget(name_lbl, idx+1, 1)

      #Buttons
      tmpView_btn = QtGui.QPushButton("View", self)
      tmpView_btn.clicked.connect(lambda: self.viewFile())
      tmpDel_btn = QtGui.QPushButton("x")
      tmpDel_btn.clicked.connect(lambda: self.delFile())
      self.grid.addWidget(tmpView_btn, idx+1, 2)
      self.grid.addWidget(tmpDel_btn, idx+1, 3)

    self.addFile_btn = QtGui.QPushButton("+")
    self.addFile_btn.clicked.connect(lambda: self.addFileForReview())
    self.grid.addWidget(self.addFile_btn, len(self.filesUnderReview)+1, 3)
    self.refresh_btn = QtGui.QPushButton(u'\u27F3')
    self.refresh_btn.clicked.connect(lambda: self.updateList())
    self.grid.addWidget(self.refresh_btn, 0, 3)

    #self.move(300, 150)
    self.setGeometry(100, 100, 10, 10)
    self.setWindowTitle('Code Review')
    self.show()
        
  def delFile(self):
    _idx = self.grid.indexOf(self.sender())
    _row = self.grid.getItemPosition(_idx)[0] - 1 #offset by 1

    #Only the submitter can delete a code review
    if (getpass.getuser() == self.filesInfo[_row][2]):
      #Also delete the tmp tree and all its contents
      self.tmp_dir = str(self.filesInfo[_row][0]).split('/')[-1] + "_" + str(self.filesInfo[_row][2])
      try:
        shutil.rmtree(self.tmp_dir)
      except:
        print "Error trying to delete temp dir: " + self.tmp_dir

      #Delete the row from the list, then write the list to the file
      del self.filesInfo[_row]
      with open("filesUnderReview.txt", 'w') as f:
        for entry in self.filesInfo:
          if (entry != []):
            _string = ','.join(entry)
            f.write("%s\n" % _string)

      self.updateList()
    else:
      print "TODO: add a dialog to tell user they can't delete a submission not created by them"

  def viewFile(self):
    _idx = self.grid.indexOf(self.sender())
    _row = self.grid.getItemPosition(_idx)[0] - 1 #offset by 1
    self.viewWidget = ViewWidget(self.filesInfo[_row])
    self.viewWidget.show()

  def updateList(self):
    self.filesUnderReview = self.getFilesUnderReview("filesUnderReview.txt")
    for i in reversed(range(self.grid.count())): 
      self.grid.itemAt(i).widget().setParent(None)
    self.initUI()

  def addFileForReview(self):
    #Opens a dialog to input:
    # - file to review
    # - file to compare to
    #   - provide default p4 filelog option (use p4 module)
    #   - option to specify another file for comparison
    # - people to add for code review (via email)
    self.addFileWidget = AddFileWidget()
    self.addFileWidget.show()
      
  def getFilesUnderReview(self, rFile):
    lines = [line.rstrip('\n') for line in open(rFile)]
    self.filesInfo = [line.split(',') for line in lines if line != ""]
    return [[line[0], line[2]] for line in self.filesInfo]
      
#=============================================================================================================
class AddFileWidget(QtGui.QWidget):
  def __init__(self):
    super(AddFileWidget, self).__init__()
    self.grid = QtGui.QGridLayout()
    self.setLayout(self.grid)

    #NOTE: if it stops working, I added 'self' arg to  self.*_lnEdit

    #Labels and Input Fields
    self.addFile_lbl = QtGui.QLabel("New File:")
    self.addFile_lnEdit = QtGui.QLineEdit(self)

    self.oldFile_lbl = QtGui.QLabel("Old File:")
    self.oldFile_lnEdit = QtGui.QLineEdit(self)
    #Radio buttons
    self.p4_chk = QtGui.QCheckBox("Latest P4 ver.", self)
    self.none_chk = QtGui.QCheckBox("None", self)
    self.other_chk = QtGui.QCheckBox("Other:", self)
    self.p4_chk.toggled.connect(lambda: self.click("p4"))
    self.none_chk.toggled.connect(lambda: self.click("none"))
    self.other_chk.toggled.connect(lambda: self.click("other"))

    self.uploader_lbl = QtGui.QLabel("Uploader:")
    self.uploader_lnEdit = QtGui.QLineEdit(getpass.getuser())
    self.addReviewers_lbl = QtGui.QLabel("Add Reviewers:")
    self.addReviewers_txtEdit = QtGui.QTextEdit(self)

    self.grid.addWidget(self.addFile_lbl, 1, 0)
    self.grid.addWidget(self.addFile_lnEdit, 1, 1)
    self.grid.addWidget(self.oldFile_lbl, 2, 0)
    self.grid.addWidget(self.p4_chk, 2,1)
    self.grid.addWidget(self.none_chk, 3,1)
    self.grid.addWidget(self.other_chk, 4, 1)
    self.grid.addWidget(self.oldFile_lnEdit, 5, 1)
    self.grid.addWidget(self.uploader_lbl, 6, 0)
    self.grid.addWidget(self.uploader_lnEdit, 6, 1)
    self.grid.addWidget(self.addReviewers_lbl, 8, 0)
    self.grid.addWidget(self.addReviewers_txtEdit, 8, 1)

    #Save and Cancel buttons
    self.save_btn = QtGui.QPushButton("Save")
    self.cancel_btn = QtGui.QPushButton("Cancel")
    self.grid.addWidget(self.save_btn, 10, 1)
    self.grid.addWidget(self.cancel_btn, 11, 1)
    self.save_btn.clicked.connect(lambda: self.saveAddFile())
    self.cancel_btn.clicked.connect(lambda: self.cancelAddFile())

    self.setGeometry(140, 140, 500, 300)
    self.setWindowTitle("Code Review - Add File for Review")

  def click(self, _type):
    if (_type == "p4"):
      self.none_chk.setChecked(False)
      self.other_chk.setChecked(False)
    elif (_type == "none"):
      self.p4_chk.setChecked(False)
      self.other_chk.setChecked(False)
    else:
      self.p4_chk.setChecked(False)
      self.none_chk.setChecked(False)


  def saveAddFile(self):
    #TODO: add error handling of sys calls
    new_file = str(self.addFile_lnEdit.text())
    uploader = str(self.uploader_lnEdit.text())

    #TODO: check that the files can be opened

    old_file = "-1"
    if (self.p4_chk.isChecked()):
      print "Chose P4"
      cmd = "p4 filelog " + str(self.addFile_lnEdit.text())
      std_out = os.popen(cmd).read()
      #Get latest p4 version from this
      std_out = std_out.split(' ')
      old_file = std_out[1]
    elif (self.none_chk.isChecked()):
      print "Chose None"
      old_file = "None"
    elif (self.other_chk.isChecked()):
      print "Other"
      old_file = str(self.oldFile_lnEdit.text())
    else:
      print "No option picked..."
    
    if (old_file != "-1"):
      #Save the info to filesForEdit
      string = new_file + "," + old_file + "," + \
               uploader + "," + self.addReviewers_txtEdit.toPlainText() + '\n'
      text_file = open("filesUnderReview.txt", 'a')
      text_file.write(string)
      text_file.close()

      #Save the relevant files to a tmp dir
      #Make a new working directory
      tmp_file_name = new_file.split('/')[-1]
      self.tmp_dir = tmp_file_name + "_" + uploader
      try:
        os.mkdir(self.tmp_dir)
      except OSError:
        print "Couldn't make directory: " + self.tmp_dir + "..."
      #Copying a copy of new file
      copy_new_file = self.tmp_dir + "/" + tmp_file_name
      shutil.copyfile(new_file, copy_new_file)
      #Copying a copy of p4 version
      if (self.p4_chk.isChecked()):
        tmp_old_file = self.tmp_dir + "/tmp_" + tmp_file_name
        cmd = "p4 print -o " + tmp_old_file + " " + new_file
        os.system(cmd)
        cmd = "diff " + tmp_old_file + " " + new_file + " > " + self.tmp_dir + "/diff.txt"
        os.system(cmd)
      elif (self.other_chk.isChecked()):
        tmp_old_file = self.tmp_dir + "/tmp_" + old_file.split('/')[-1]
        try:
          shutil.copyfile(old_file, tmp_old_file)
        except IOError, e:
          print "Unable to copy file " + old_file + " to " + tmp_old_file + ". %s" %e
        cmd = "diff " + tmp_old_file + " " + copy_new_file + " > " + self.tmp_dir + "/diff.txt"
        os.system(cmd)
      else:
        #None was picked, and there is no other file to copy
        pass


      #TODO: Send email to reviewers that there is a code review waiting for them

      self.close()
    #Do nothing if an option for old_file hasn't been picked

  def cancelAddFile(self):
    self.close()

#=============================================================================================================
class ViewWidget(QtGui.QWidget):
  def __init__(self, fileInfo):
    super(ViewWidget, self).__init__()

    #Grid Setup
    self.grid = QtGui.QGridLayout()
    self.setLayout(self.grid)
    self.grid.setRowStretch(0, 1)
    self.grid.setRowStretch(1, 12)
    self.grid.setColumnStretch(0, 4)
    self.grid.setColumnStretch(1, 4)
    self.grid.setColumnStretch(2, 4)

    #Variables
    self.tmp_dir = fileInfo[0].split('/')[-1] + "_" + fileInfo[2]
    fileToReview = self.tmp_dir + "/" + fileInfo[0].split('/')[-1]
    self.addingCommentFlag = False
    self.currentUser = getpass.getuser()
    self.searchLines = [] #This will store line numbers that 'n' and 'shift+n' will jump to
    self.currentLnComments = []

    #Depending on file to compare to (prev. p4 version, none, or specific) need to organize differently
    #File under edit
    self.new_text = QtGui.QPlainTextEdit(self)
    highlight = syntax.PythonHighlighter(self.new_text.document())
    self.text = open(fileToReview).read()
    self.new_text.setPlainText(self.text)
    self.new_text.setReadOnly(True)
    self.new_text.setLineWrapMode(0)
    self.grid.addWidget(self.new_text, 1, 1)
    self.prevLinePtr = 0 #used to revert font from bold
    self.currentLinePtr = 0
    self.n_newLines = self.new_text.blockCount()

    self.updateCommentsDS()
    self.drawRHSPanel()

    #Set up old file (if applicable)
    fileToCompare = ""
    if (fileInfo[1] == "None"):
      fileToCompare = "None"
    elif (fileInfo[1][0] == "#"):
      fileToCompare = self.tmp_dir + "/tmp_" + fileInfo[0].split('/')[-1]
    else:
      fileToCompare = self.tmp_dir + "/tmp_" + fileInfo[1].split('/')[-1]
      self.oldFile_lbl = QtGui.QLabel(self)
      self.oldFile_lbl.setText(fileInfo[1].split('/')[-1])
      self.grid.addWidget(self.oldFile_lbl, 0, 0)

    #Labels for the boxes
    self.newFile_lbl = QtGui.QLabel(self)
    self.newFile_lbl.setText(fileInfo[0].split('/')[-1])
    self.comments_lbl = QtGui.QLabel(self)
    self.comments_lbl.setText("Comments:")
    self.grid.addWidget(self.newFile_lbl, 0, 1)
    self.grid.addWidget(self.comments_lbl, 0, 2)
    

    #Highlighter =====================================================================================
    #First read the diff file
    diffFile = self.tmp_dir + "/diff.txt"
    diffTxt = [line.rstrip('\n') for line in open(diffFile)]
    print diffTxt

    #Set up highlighter object
    #fmt_minus = QtGui.QTextCharFormat()
    #fmt_minus.setUnderlineColor(QtGui.QColor(255, 204, 204))
    #fmt_minus.setUnderlineStyle(QtGui.QTextCharFormat.SpellCheckUnderline)      
    self.format_unselected = QtGui.QTextCharFormat()
    self.format_unselected.setFontWeight(QtGui.QFont.Normal)
    self.format_selected = QtGui.QTextCharFormat()
    self.format_selected.setFontWeight(QtGui.QFont.Bold)
    self.makeCurrentLnBold()

    self.format_minus = QtGui.QTextCharFormat()
    self.format_minus.setBackground(QtGui.QBrush(QtGui.QColor(250, 128, 114)))
    #fmt_plus = QtGui.QTextCharFormat()
    #fmt_plus.setUnderlineColor(QtGui.QColor(255, 204, 204))
    #fmt_plus.setUnderlineStyle(QtGui.QTextCharFormat.SpellCheckUnderline)        
    self.format_plus = QtGui.QTextCharFormat()
    self.format_plus.setBackground(QtGui.QBrush(QtGui.QColor(50, 205, 50)))

    if (fileToCompare != "None"):
      #Set up objects
      self.old_text = QtGui.QPlainTextEdit()
      highlight = syntax.PythonHighlighter(self.old_text.document())
      self.text = open(fileToCompare).read()
      self.old_text.setPlainText(self.text)
      self.old_text.setReadOnly(True)
      self.old_text.setLineWrapMode(0)
      #self.new_text.clicked.connect(lambda: self.mousePressEvent("old"))
      self.grid.addWidget(self.old_text, 1, 0)
      self.old_text.horizontalScrollBar().valueChanged.connect(self.new_text.horizontalScrollBar().setValue)
      self.old_text.verticalScrollBar().valueChanged.connect(self.new_text.verticalScrollBar().setValue)
      self.new_text.horizontalScrollBar().valueChanged.connect(self.old_text.horizontalScrollBar().setValue)
      self.new_text.verticalScrollBar().valueChanged.connect(self.old_text.verticalScrollBar().setValue)

      #Highlight the portions recorded in the diff file
      reds = []
      greens = []
      #NOTE: The number to highlight in red is everything before the letter, the number to highlight in green is after
      for i in range(len(diffTxt)):
        line = diffTxt[i]
        if (i > 0):
          prev_line = diffTxt[i-1]

        if  (line[0].isdigit()):
          bits = re.findall(r"[^\W\d_]+|\d+", line)
          gettingReds = True
          for bit in bits:
            if (bit.isdigit()):
              if (gettingReds):
                reds.append(int(bit))
              else:
                greens.append(int(bit))
            else:
              gettingReds = False

      #Now do all the highlighting
      for red in reds:
        block = self.old_text.document().findBlockByLineNumber(red-1)
        blockPos = block.position()
        cursor = QtGui.QTextCursor(self.old_text.document())
        cursor.setPosition(blockPos)
        cursor.movePosition(QtGui.QTextCursor.EndOfBlock, 1)
        cursor.mergeCharFormat(self.format_minus)
      for green in greens:
        block = self.new_text.document().findBlockByLineNumber(green-1)
        blockPos = block.position()
        cursor = QtGui.QTextCursor(self.new_text.document())
        cursor.setPosition(blockPos)
        cursor.movePosition(QtGui.QTextCursor.EndOfBlock, 1)
        cursor.mergeCharFormat(self.format_plus)

    #Draw the info panel

    self.move(200, 150)
    self.resize(1400, 800)
    self.setWindowTitle('Code Review - View File')

  #Input Stuff =====================================================================================
  def mousePressEvent(self, event):
    if (event.button() == 2): #right click
      cursor = QtGui.QCursor()

  def keyPressEvent(self, event):
    key = event.key()
    #print key
    fn = self.keys_to_fns(key)
    fn()

  def keys_to_fns(self, key):
    return {
      72:       self.h,
      74:       self.j,
      75:       self.k,
      76:       self.l,
      #78:       self.n,
      16777248: self.shift,
      16777220: self.enter,
      16777216: self.esc,
    } [key]

  def h(self):
    self.new_text.horizontalScrollBar().setValue(self.new_text.horizontalScrollBar().minimum())

  def l(self):
    if (self.new_text.horizontalScrollBar().maximum() >= self.old_text.horizontalScrollBar().maximum()):
      self.old_text.horizontalScrollBar().setValue(self.old_text.horizontalScrollBar().maximum())
    else:
      self.old_text.horizontalScrollBar().setValue(self.old_text.horizontalScrollBar().maximum())

  def j(self):
    print self.old_text.verticalScrollBar().value()
    self.old_text.verticalScrollBar().setValue(self.old_text.verticalScrollBar().value() + 1)
    self.prevLinePtr = self.currentLinePtr
    self.currentLinePtr = (self.currentLinePtr+1) if (self.currentLinePtr < (self.n_newLines-1)) else (self.n_newLines-1)
    self.makeCurrentLnBold()
    self.drawRHSPanel()
    #print "currentLinePtr:", self.currentLinePtr

  def k(self):
    self.prevLinePtr = self.currentLinePtr
    self.currentLinePtr = (self.currentLinePtr-1) if (self.currentLinePtr > 0) else 0
    self.makeCurrentLnBold()
    self.drawRHSPanel()
    #print "currentLinePtr:", self.currentLinePtr

  def n(self):
    pass

  def shift(self):
    pass

  def enter(self):
    #Enter to add a new comment
    if (not self.addingCommentFlag):
      self.addingCommentFlag = True
      #Draw the input stuff
      self.commentsInputBox_txtEdit = QtGui.QTextEdit(self)
      self.grid.addWidget(self.commentsInputBox_txtEdit, 1, 2)
      #Cancel and submit buttons
      self.cancelComment_btn = QtGui.QPushButton("Cancel", self)
      self.cancelComment_btn.clicked.connect(lambda: self.esc())
      self.submitComment_btn = QtGui.QPushButton("Submit", self)
      self.submitComment_btn.clicked.connect(lambda: self.saveComment())
      self.grid.addWidget(self.submitComment_btn, 3, 2)
      self.grid.addWidget(self.cancelComment_btn, 4, 2)

  def esc(self):
    if (self.addingCommentFlag):
      #Remove the input box, save, and cancel buttons
      #TODO: Write a helper function to pass object and delete it
      self.grid.removeWidget(self.commentsInputBox_txtEdit)
      self.commentsInputBox_txtEdit.deleteLater()
      self.grid.removeWidget(self.cancelComment_btn)
      self.cancelComment_btn.deleteLater()
      self.grid.removeWidget(self.submitComment_btn)
      self.submitComment_btn.deleteLater()

    self.addingCommentFlag = False

  def shift(self):
    pass

  #Button Fns ======================================================================================
  def saveComment(self):
    commentsFile = self.tmp_dir + "/comments_" + self.currentUser + ".txt"
    ts = str(calendar.timegm(time.gmtime())) + "\n"
    text = "<" + str(self.currentLinePtr) + "\n" + self.commentsInputBox_txtEdit.toPlainText() + "\n>" + ts
    fh = open(commentsFile, "a+")
    fh.write(text)
    fh.close()
    #Now get rid of the input stuff
    self.esc()
    #Also update the comments DS
    self.updateCommentsDS()
    pass

  #def cancelComment(self):
  #  NOTE: redundant
  #  self.esc()

  #Helper Draw Fns =================================================================================
  def drawRHSPanel(self):
    #Delete all entries of comment_lbls

    #For init, self.commentsWidget won't exist
    try:
      self.grid.removeWidget(self.commentsWidget)
      self.commentsWidget.deleteLater()
    except:
      pass

    self.currentLnComments = [] #Clearing list

    #Check to see if there are any comments
    if (not self.comments[self.currentLinePtr]):
      pass
    else:
      for comment in self.comments[self.currentLinePtr]:
        self.currentLnComments.append(comment)
    self.commentsWidget = CommentsWidget(self.currentLnComments, self.addingCommentFlag)
    self.grid.addWidget(self.commentsWidget, 1, 2)

  def makeCurrentLnBold(self):
    #make the previous line normal
    block = self.new_text.document().findBlockByLineNumber(self.prevLinePtr)
    blockPos = block.position()
    cursor = QtGui.QTextCursor(self.new_text.document())
    cursor.setPosition(blockPos)
    cursor.movePosition(QtGui.QTextCursor.EndOfBlock, 1)
    cursor.mergeCharFormat(self.format_unselected)
    
    #make the new line 
    block = self.new_text.document().findBlockByLineNumber(self.currentLinePtr)
    blockPos = block.position()
    cursor = QtGui.QTextCursor(self.new_text.document())
    cursor.setPosition(blockPos)
    cursor.movePosition(QtGui.QTextCursor.EndOfBlock, 1)
    cursor.mergeCharFormat(self.format_selected)

  #Helper Fns ======================================================================================
  def updateCommentsDS(self):
    def takeThird(elem):
      return elem[2]

    #Read all comments
    #TODO: sort comments by date
    self.comments = [[] for _ in range(self.n_newLines)]
    commentFiles = [f for f in os.listdir(self.tmp_dir) if re.match("comment_*", f)]
    for commentFile in commentFiles:
      #Read each comment into a list (maybe I want it as a tuple?)
      tmp_filePath = self.tmp_dir + "/" + commentFile
      tmp_commenter = commentFile.split('_')[-1][:-4] #lop off the ".txt" at the end
      tmp_str = ""
      tmp_lineNo = 0
      tmp_ts = 0
      with open(tmp_filePath, 'r') as f:
        for line in f:
          if (line[0] == '<'):
            #indicator that we are reading a new comment
            #Save the line number
            tmp_lineNo = int(line[1:])
          elif  (line[0] == '>'):
            #indicator that we've finished reading a comment
            tmp_ts = line[1:].rstrip()
            self.comments[int(tmp_lineNo)].append((tmp_commenter, tmp_str, tmp_ts))
            self.comments[int(tmp_lineNo)].sort(key=takeThird, reverse=True)
            #Reset variables
            tmp_str = ""
            tmp_lineNo = 0
            tmp_ts = 0
          else:
            #is a comment
            tmp_str += line

#=============================================================================================================
class CommentsWidget(QtGui.QWidget):
  def __init__(self, currentLnComments, addingCommentFlag):
    super(CommentsWidget, self).__init__()

    #Grid Setup
    self.grid = QtGui.QGridLayout()
    self.setLayout(self.grid)
    self.grid.setColumnStretch(0, 3)
    if (addingCommentFlag):
      self.grid.setRowStretch(0, 2)
      self.grid.setRowStretch(1, 1)
      self.grid.setRowStretch(2, 4)
    else:
      self.grid.setRowStretch(0, 3)
    
    self.comment_lbls = []
    _string = ""
    if (not currentLnComments):
      _string = "No comments."
    else:
      _ctr = 2
      for comment in currentLnComments:
        #comment format: (<name>, <comment>, <timestamp>)
        self.comment_lbls.append(QtGui.QLabel(self))
        _readable_date = time.ctime(float(comment[2]))
        _string += comment[0] + " on " + _readable_date + "\n" + comment[1]
        _string += "===================================\n"
    self.comments_txt = QtGui.QPlainTextEdit(self)
    self.comments_txt.setPlainText(_string)
    self.comments_txt.setReadOnly(True)

    if (addingCommentFlag):
      self.grid.addWidget(self.comments_txt, 2, 0)
    else:
      self.grid.addWidget(self.comments_txt, 0, 0)


    self.show()


def main():
  app = QtGui.QApplication(sys.argv)
  ex = FormWidget()
  sys.exit(app.exec_())


if __name__ == '__main__':
  main()
