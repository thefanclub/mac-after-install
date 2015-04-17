#!/usr/bin/env python
#
# Mac After Install 
#
# Version :  1.1 beta
#
# By The Fan Club (c) 2013-2015
# 
# http://www.thefanclub.co.za
#
### BEGIN LICENSE
# Copyright (c) 2015, The Fan Club <info@thefanclub.co.za>
# The Software and any authorized copies that you make are the intellectual property of and are owned by
# The Fan Club. The structure, organization, and source code of the Software
# are the valuable trade secrets and confidential information of The Fan Club.
# The Software is protected by law, including but not limited to the copyright laws of the United States and
# other countries, and by international treaty provisions. Except as expressly stated herein, this agreement
# does not grant you any intellectual property rights in the Software and all rights not expressly granted are
# reserved by The Fan Club.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranties of
# MERCHANTABILITY, SATISFACTORY QUALITY, or FITNESS FOR A PARTICULAR
# PURPOSE.
#
### END LICENSE
#
from xml.dom import minidom
import os
import sys
import subprocess
import time
import datetime
import shutil
import urllib2
import webbrowser
import fcntl
import threading
import platform
from Tkinter import *
from ttk import *
import tkMessageBox
import math
import locale
import plistlib

class VerticalScrolledFrame(Frame):
    """
    * Use the 'interior' attribute to place widgets inside the scrollable frame
    * Construct and pack/place/grid normally
    * This frame only allows vertical scrolling
    """
    def __init__(self, parent, *args, **kw):
        Frame.__init__(self, parent, *args, **kw)            

        # create a canvas object and a vertical scrollbar for scrolling it
        global canvas
        vscrollbar = Scrollbar(self, orient=VERTICAL)
        vscrollbar.pack(fill=Y, side=RIGHT, expand=FALSE)
        canvas = Canvas(self, bd=0, highlightthickness=0,
                        yscrollcommand=vscrollbar.set)
        canvas.pack(side=LEFT, fill='both', expand=TRUE)
        canvas.configure(background=defaultColor)

        vscrollbar.config(command=canvas.yview)

        # reset the view
        canvas.xview_moveto(0)
        canvas.yview_moveto(0)

        # create a frame inside the canvas which will be scrolled with it
        self.interior = interior = Frame(canvas)
        interior_id = canvas.create_window(0, 0, window=interior, anchor=NW)
       
        # track changes to the canvas and frame width and sync them,
        # also updating the scrollbar
        def _configure_interior(event):
            # update the scrollbars to match the size of the inner frame
            size = (interior.winfo_reqwidth(), interior.winfo_reqheight())
            canvas.config(scrollregion="0 0 %s %s" % size)
            if interior.winfo_reqwidth() != canvas.winfo_width():
                # update the canvas's width to fit the inner frame
                canvas.config(width=interior.winfo_reqwidth())
        interior.bind('<Configure>', _configure_interior)

        def _configure_canvas(event):
            if interior.winfo_reqwidth() != canvas.winfo_width():
                # update the inner frame's width to fill the canvas
                canvas.itemconfigure(interior_id, width=canvas.winfo_width())
        canvas.bind('<Configure>', _configure_canvas)
        

def closeWindow(widget, event, window):
    # Close window
    widget.destroy()
    # Exit
    sys.exit()

    
def debugPrint(textToPrint):
    if verboseDebug:
      print textToPrint    


def appendToLog(content):
    timeStamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    writeToFile(logFile, ('['+timeStamp+']'+' '+content+'\n'), 'a')
    return


def datestampConvert(datestamp):
    try:
      dtFormat = "%Y%m%d%H%M%S"
      dtString = str(datestamp)
      dtConverted = datetime.datetime.strptime(dtString, dtFormat)
      # Localise date and time
      dtLocaleDate = locale.nl_langinfo(locale.D_FMT)
      dtLocaleTime = locale.nl_langinfo(locale.T_FMT)
      dtShow = dtConverted.strftime(dtLocaleDate)
    except:
      # Could not get datestamp from file
      dtShow='-'
    return dtShow


def checkInternetConnection(targetUrl):
    try:
        response=urllib2.urlopen(targetUrl, timeout=4)
        debugPrint("[Notice] Internet Connection Active")
        appendToLog("[Notice] Internet Connection Active")
        return True
    except:
        debugPrint("[Error] "+targetUrl+" Offline")
        appendToLog("[Error] "+targetUrl+" Offline")
        return False


def readRemoteFile(url):
    # Read contents of remote file
    try:
      wp = urllib2.urlopen(url)
      remoteContent = wp.read()
      remoteContent = remoteContent.strip()
      wp.close()
    except:
      debugPrint("[Error] Cannot read Remote Version File "+url)
      appendToLog("[Error] Cannot read Remote Version File "+url)
      remoteContent = 0 
    return remoteContent


def humanSize(num):
    for x in ['bytes','KB','MB','GB']:
      if num < 1004.0:
        return "%3.1f %s" % (num, x)
      num /= 1000.0
    return "%3.1f%s" % (num, 'TB')


def writeToFile(fileName,content,flag):
    try:
      fp = open(fileName, flag)
      fp.write(content)
      fp.close()
    except IOError:
      writeError="File Not Saved"
    except:
      writeError="File Not Saved"
      raise
    return


def deleteFile(filepath, filename):
    try:
        # Remove file
        if os.path.exists(filepath):
          os.remove(filepath)
        
        debugPrint("[Notice] %s Deleted" % filename )
        appendToLog("[Notice] %s Deleted" % filename )
    except:
        debugPrint("[Error] Could not delete %s" % filename )
        appendToLog("[Error] Could not delete %s" % filename )


def downloadTxtFile(url, localdir):
    # Download to instalDir
    try:
      webFile = urllib2.urlopen(url)
      outFileName = url.split('/')[-1]
      outFile = os.path.join(localdir,outFileName)
      localFile = open(outFile, 'w')
      localFile.write(webFile.read())
      webFile.close()
      localFile.close()
    except:
      debugPrint("[Error] Cannot download file "+url)
      appendToLog("[Error] Cannot download file "+url)
      

def downloadFile(url, localdir, item, proginc):
    # Get Current HeaderProgress
    currentHeaderProgress = headerProgPercent.get()
    # Create dir if does not exist
    if not os.path.exists(localdir):
      os.mkdir(localdir)
            
    # Download to localDir
    try:
      txData = None
      txHeaders = {   
        'User-Agent': 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)',
        'Accept-Language': 'en-us',
        'Accept-Encoding': 'gzip, deflate, compress;q=0.9',
        'Keep-Alive': '300',
        'Connection': 'keep-alive',
        'Cache-Control': 'max-age=0',
      } 
      request = urllib2.Request(url, txData, txHeaders)
      webFile = urllib2.urlopen(request)
      outFileName = url.split('/')[-1]
      # replace %20 in url with spaces in filesname
      outFileName = outFileName.replace('%20', ' ')
      outFile = os.path.join(localdir,outFileName)

      localFile = open(outFile, 'wb')

      try:
        totalSize = webFile.info().getheader('Content-Length').strip()
        debugPrint("[Notice] Download file size : "+str(totalSize))
        appendToLog("[Notice] Download file size : "+str(totalSize))   
        header = True
      except AttributeError:
        header = False # a response doesn't always include the "Content-Length" header
        debugPrint("[Error] No Header for "+url)
        appendToLog("[Error] No Header for "+url)        
      if header:
        totalSize = int(totalSize)

      totalDownloaded = 0

      while True:
        buffer = webFile.read(8192)
        if not buffer:
          sys.stdout.write('\n')
          break

        totalDownloaded += len(buffer)
        localFile.write(buffer)
        if not header:
          totalSize = totalDownloaded # unknown size

        percent = float(totalDownloaded) / totalSize
        percent = round(percent*100, 2)
        #sys.stdout.write("Downloaded %d of %d bytes (%0.2f%%)\r" % (totalDownloaded, totalSize, percent))
        progress = round(percent) / 2

        itemProgressPercent[item].set(progress)
        headerProgPercent.set(setHeaderProgress(item, proginc, currentHeaderProgress))
        headerProgLabelTxt.set("Downloading "+titleList[item]+" ... "+str(humanSize(totalDownloaded))+" / "+str(humanSize(totalSize)))

      webFile.close()
      localFile.close()
    except:
      debugPrint("[Error] Cannot download file "+url)
      appendToLog("[Error] Cannot download file "+url)


def readFile(filepath):
    try:
      fp = open(filepath, 'r' )
      output = fp.read()
      output = output.strip()
      fp.close()
      return output
    except:
      debugPrint("[Error] Cannot read Local Version File")
      appendToLog("[Error] Cannot read Local Version File")


def checkListUpdate():
    global localVersion
    # Get local list version
    localVersion = readFile(localVersionPath)
    if not localVersion :
      localVersion = 0
      
    # Update Progressbar
    splashProgressPercent.set(40)
    refreshGui(splashWindow)
    
    # Get remote list version
    if checkInternetConnection('http://thefanclub.co.za') == True:
      # ONLINE
      remoteVersion = readRemoteFile(remoteVersionPath)
    else:
      # OFFLINE
      remoteVersion = 0  

    # Update Progressbar
    splashProgressPercent.set(50)
    refreshGui(splashWindow)
      
    # Decide to update list or not
    if remoteVersion > localVersion :
      debugPrint("[Notice] Downloading new software list "+remoteVersion)
      appendToLog("[Notice] Downloading new software list "+remoteVersion)
      splashProgressPercent.set(60)
      refreshGui(splashWindow)
      # Download new version
      downloadTxtFile(remoteVersionPath, installDir)
      # Download new XML list
      downloadTxtFile(remoteXmlPath, installDir)
      localVersion = remoteVersion
      
      
def on_cell_toggle():
    # Toggle if not busy installing
    if installStatus != 'busy' and installStatus != 'complete' :
      # Count items
      itemCount = len(titleList)

      # check Checkboxes one by one for change
      for listItem in range(itemCount): 
        itemInstallState = installStateList[listItem]
        
        # Set icon depending on state
        if itemInstallState == 'installed': 
          if checkItem[listItem].get() == 1 :
            iconPathMod = iconPathReinstall
        
          if checkItem[listItem].get() == 0 :
            iconPathMod = iconPathOk

          # Set icon     
          itemIconImage[listItem] = PhotoImage(file=iconPathMod)
          itemIcon[listItem].configure(image=itemIconImage[listItem])
          itemIcon[listItem].image = itemIconImage[listItem]


def refreshGui(widget):
     widget.update()
     widget.update_idletasks()

          
def setHeaderProgress(item, proginc, currentprogress):
    newHeaderProgress = currentprogress + (float(itemProgressPercent[item].get()) / 100 * proginc )
    return newHeaderProgress


def on_install_button_active(button, model, selectcount):
    # Main install Section
    global pulseTimer
    global installStatus
    global itemIconImage
    global view
    global p1

    # set busy flag
    installStatus = 'busy'

    # Count items
    itemCount = len(titleList)

    # Disable Checkboxes
    for listItem in range(itemCount):
      itemCheckBox[listItem].configure(state=DISABLED) 
        
    # START installing apps one by one 

    # using itemSelectCount to do progress increments
    progInc = float(100 / selectcount) 
    itemIncCount = 0
    
    headerProgPercent.set(0)

    for listItem in range(itemCount):
      # Check which items are selected True in list column 0
      itemSelected = checkItem[listItem].get()
      if itemSelected == 1:
        # set currentHeaderProgress for each process at start
        currentHeaderProgress = headerProgPercent.get()

        # With selected items ...
        headerLabelTxt.set('Installing Software '+str(itemIncCount+1)+' of '+str(selectcount))
        appendToLog('[Notice] Installing Software '+str(itemIncCount+1)+' of '+str(selectcount))

        # Start Install software         
        installError = ''   
        
        headerProgLabelTxt.set("Installing "+titleList[listItem])
        debugPrint("Installing %s" % titleList[listItem])
        appendToLog("Installing %s" % titleList[listItem])

        # Get local filename and replace %20 in url with spaces
        outFileName = urlList[listItem].split('/')[-1]
        outFileExt = os.path.splitext(outFileName)[1][1:]
        outFileName = outFileName.replace('%20', ' ')
        outFile = os.path.join(localDownloads,outFileName)
        outFileTmp = os.path.join(localDownloads, '__MACOSX')
        
        # Download Install file
        if outFileName:
          try:
            if not os.path.exists(outFile):
              headerProgLabelTxt.set("Downloading "+titleList[listItem]+" ...")
              debugPrint("[Notice] Download started for %s" % titleList[listItem] )
              appendToLog("[Notice] Download started for %s" % titleList[listItem] )
              # Replace any spaces in url with %20 
              downloadFile(urlList[listItem].replace(' ', '%20'), localDownloads, listItem, progInc)
            else:
              itemProgressPercent[listItem].set(50) 
              headerProgPercent.set(setHeaderProgress(listItem, progInc, currentHeaderProgress))

          except:
            debugPrint("[Error] Download failed for %s" % titleList[listItem] )
            appendToLog("[Error] Download failed for %s" % titleList[listItem] )
            installError = "[Error] Download failed for " + titleList[listItem]
        else:
            debugPrint("[Error] No download link for %s" % titleList[listItem] )
            appendToLog("[Error] No download link for %s" % titleList[listItem] )
            installError = "[Error] No download link for " + titleList[listItem]            
        
        # Mount DMG or extract gz tar bz2 if downloaded
        devicePath = ''
        mountPoint = ''
        if os.path.exists(outFile) and outFileName:
          if outFileExt.lower() == 'dmg':
            # DMG files
            try:
              # Mount DMG with hdiutil in background without opening in /Volumes 
              headerProgLabelTxt.set("Verifying "+outFileName+" ...")
              bashCommand="hdiutil mount %s -noautoopen -noautoopenro -nobrowse | tail -1" % outFile.replace(' ', '\ ')
              p1 = subprocess.Popen( bashCommand, shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE )
              output = p1.communicate()[0]
                     
              # check results of output
              if 'failed' not in output :
                # Split output on Tabs
                outputParse = output.split('\t')
                # Get Device & Mount point
                devicePath = outputParse[0].rstrip()
                mountPoint = outputParse[2].rstrip()
                
                itemProgressPercent[listItem].set(70)
                headerProgPercent.set(setHeaderProgress(listItem, progInc, currentHeaderProgress))
  
                debugPrint("[Notice] Mounted %s" % outFile )
                appendToLog("[Notice] Mounted %s" % outFile )
              else :
                raise
            
            except:
              debugPrint("[Error] Could not Mount %s" % outFile )
              appendToLog("[Error] Could not Mount %s" % outFile )
              installError = "[Error] Could not Mount %s" % outFile
              deleteFile(outFile, outFileName)

          if outFileExt.lower() in ('bz', 'tgz', 'tar', 'gz', 'bz2', 'zip'):
            # TAR BZ GZ ZIP Files
            try:
              # Extract files 
              headerProgLabelTxt.set("Extracting "+outFileName+" ...")
              if outFileExt.lower() == 'zip':
                bashCommand="unzip -q -o %s -d %s" % (outFile.replace(' ', '\ '),localDownloads)
              else:
                bashCommand="tar -xf %s -C %s" % (outFile.replace(' ', '\ '),localDownloads)
              p1 = subprocess.Popen( bashCommand, shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE )
              output = p1.communicate()[0]
                     
              # check results of output
              if output :
                raise
              else:
                debugPrint("[Notice] Extracted %s" % outFile )
                appendToLog("[Notice] Extracted %s" % outFile )
            except:
              debugPrint("[Error] Could not extract %s" % outFile )
              appendToLog("[Error] Could not extract %s" % outFile )
              installError = "[Error] Could not extract %s" % outFile
              deleteFile(outFile, outFileName)

        # Copy app file to Applications id DMG is mounted OR extracted file is a .app or normal folder
        if os.path.exists(mountPoint) or os.path.exists(os.path.join(localDownloads,appFileList[listItem])):
          headerProgLabelTxt.set("Installing "+titleList[listItem]+" ...")
          # Get app name from mounted DMG rather TODO

          # Downloaded Applications folder path 
          if outFileExt.lower() == 'dmg':
            # Mounted DMG folder path
            appFilePath = os.path.join(mountPoint,appFileList[listItem])
            
          if outFileExt.lower() in ('bz', 'tar', 'tgz', 'gz', 'bz2', 'zip'):
            # Extracted app folder path
            appFilePath = os.path.join(localDownloads,appFileList[listItem])
  
          # Applications Install folder path
          appInstallPath = os.path.join(appsFolder,appFileList[listItem])
          
          # Check if app is running and ask to close
          appFileBash = appFileList[listItem].replace(" ", "\ ")
          bashCommand="ps aux | grep %s | grep '[A]pplications' | awk '{print $2}' | xargs" % appFileBash
          p1 = subprocess.Popen( bashCommand, shell=True, stdout=subprocess.PIPE )
          output = p1.communicate()[0]

          if output :
            appPids=output
            # Render Close App Dialog
            renderAppClose(titleList[listItem], appPids)          
          
          # Copy app file  
          try:
              # Remove app folder if present
              if os.path.exists(appInstallPath):
                shutil.rmtree(appInstallPath)
              # Copy app folder recursively
              if outFileExt.lower() == 'dmg':
                bashCommand="cp -R %s %s" %( appFilePath.replace(' ', '\ '), appInstallPath.replace(' ', '\ ') )
              if outFileExt.lower() in ('bz', 'tar', 'tgz', 'gz', 'bz2', 'zip'):
                bashCommand="mv %s %s" %( appFilePath.replace(' ', '\ '), appInstallPath.replace(' ', '\ ') )
              p1 = subprocess.Popen( bashCommand, shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE )
              output = p1.communicate()[0]
              
              if output:
                raise
              else:
                itemProgressPercent[listItem].set(90) 
                headerProgPercent.set(setHeaderProgress(listItem, progInc, currentHeaderProgress))            
                debugPrint("[Notice] Copied %s to Applications" % appFilePath )
                appendToLog("[Notice] Copied %s to Applications" % appFilePath )  
          except:
              debugPrint("[Error] Could not copy %s to Applications" % appFilePath )
              appendToLog("[Error] Could not copy %s to Applications" % appFilePath )
              installError = "[Error] Could not copy %s to Applications" % appFilePath

          # Check if app file exists in Applications after copy
          if os.path.exists(appInstallPath) and not installError :
              debugPrint("[Notice] %s installed" % titleList[listItem] )
              appendToLog("[Notice] %s installed" % titleList[listItem] )
          else:
              debugPrint("[Error] Could not install %s" % titleList[listItem] )
              appendToLog("[Error] Could not install %s" % titleList[listItem] )
              installError = "[Error] Could not install %s" % titleList[listItem]
              
          # Set ownership of app folder to current user not root
          if os.path.exists(appInstallPath):
            try:
              bashCommand="chown -R '%s' '%s'" % (os.getlogin(),appInstallPath)
              p1 = subprocess.Popen( bashCommand, shell=True, stdout=subprocess.PIPE )
              output = p1.communicate()[0]
            except:
              debugPrint("[Warning] Could set user permissions on %s" % appInstallPath )
              appendToLog("[Warning] Could set user permissions on %s" % appInstallPath )
              
          # Unmount DMG 
          if outFileExt.lower() == 'dmg':
            try:
              bashCommand="hdiutil detach %s | tail -1" % devicePath
              p1 = subprocess.Popen( bashCommand, shell=True, stdout=subprocess.PIPE )
              output = p1.communicate()[0]
              if 'ejected' in output:
                debugPrint("[Notice] %s unmounted" % outFileName )
                appendToLog("[Notice] %s unmounted" % outFileName)
              else:
                raise           
                
            except:
              debugPrint("[Warning] Could not unmount %s" % devicePath )
              appendToLog("[Warning] Could not unmount %s" % devicePath )

          # Delete zip extra folders if present
          if os.path.exists(outFileTmp):
            shutil.rmtree(outFileTmp)
            
          # Cleanup Delete downloaded file TODO - remove comment for production
          #deleteFile(outFile, outFileName)
             
        # END of main item Install 
        
        # De-select checkbox
        checkItem[listItem].set(0)
    
        # Check if install ok and set icon and progress bar
        if installError == '':
          iconPathMod = iconPathOk
          installStateList[listItem]='installed'
          itemProgressPercent[listItem].set(100) 
          headerProgPercent.set(setHeaderProgress(listItem, progInc, currentHeaderProgress))
        else:
          iconPathMod = iconPathError
          installStateList[listItem]='error'
          debugPrint("[Error] Installation failed : %s" % installError )
          appendToLog("[Error] Installation failed : %s" % installError)
          itemProgressPercent[listItem].set(100)
          headerProgPercent.set(setHeaderProgress(listItem, progInc, currentHeaderProgress))
          # Set to 0 after main progress update
          itemProgressPercent[listItem].set(0)
         
        # Set icon     
        itemIconImage[listItem] = PhotoImage(file=iconPathMod)
        itemIcon[listItem].configure(image=itemIconImage[listItem])
        itemIcon[listItem].image = itemIconImage[listItem]
        
        # If selected Inc for each item as we know not how many here
        # Move progress incrementally depending on number of install items
        itemIncCount = itemIncCount + 1
        displayInc = progInc * itemIncCount

        # Update main progress bar at the end of each item install
        headerProgPercent.set(displayInc)

    # All Software Install Done - The End -

    headerProgPercent.set(100)
    headerProgLabelTxt.set('')
    
    headerLabelTxt.set('Installation Complete')
    debugPrint('[END] Installation Complete')
    appendToLog('[END] Installation Complete')

    # Reset installstatus
    installStatus = 'complete'
    # Remove Cancel Button 
    cancelButton.destroy()
 
    # Activate Install Now/Done button 
    installButton.configure(state=NORMAL)


def on_install_thread():
    global loop_thread
    global installButtonTxt

    # If button set active and label set to done exit
    if installButtonTxt == 'Done':
       sys.exit()

    appendToLog('Install sequence initiated - Install Now')

    # Count items before we start
    itemCount = len(titleList)     
    # count selected items    
    itemSelectCount = 0
    for listItem in range(itemCount):
      # Check which items are selected use get to get VarInt variable instance value
      itemSelected = checkItem[listItem].get()
      if itemSelected == 1:
        itemSelectCount = itemSelectCount + 1
        
    debugPrint('Number of items selected for install : %s' % str(itemSelectCount))
    appendToLog('Number of items selected for install : %s' % str(itemSelectCount))
    
    # Do nothing if no items selected
    if itemSelectCount == 0 :
      return                 
       
    # Set button and progress
    installButtonTxt = "Done"
    installButton.configure(text=installButtonTxt)
    installButton.configure(state=DISABLED)
    headerProgPercent.set(5)
    
    headerLabelTxt.set('Installing new software ...')
    headerProgLabelTxt.set('Installation Started')
    
    appendToLog("Installing new software ...")

    # Main Install Thread Loop
    loop_thread = threading.Thread(target=on_install_button_active, args=['button', 'model', itemSelectCount])
    # Start Thread as Daemon - so that all threads terminate when window closes or user cancels and quits
    loop_thread.daemon = True
    # Start Main Install Threaded
    loop_thread.start()
    
    appendToLog('Install Thread started')


def joinTreads():
    global loop_thread
    # Join Threads every second for 0.5 sec and relax
    try:
      loop_thread.join(timeout=0.02)
    except:
      debugPrint('[Error] Cannot Join Threads')
      appendToLog('[Error] Cannot Join Threads')
    return True


def renderCancelDialog():
    global installStatus
    if tkMessageBox.askyesno(appName, "Are you sure you would like to Quit?", icon='question'):
      if loop_thread :  
        joinTreads()    
      mainWindow.destroy()
      sys.exit()    
    return

    
def renderPlatformDialog():
    if tkMessageBox.showinfo(appName, "Only 64bit versions of Mac OS X supported", icon='warning'):
      splashWindow.destroy()
      sys.exit()  


def renderAppClose(appname, pids):
    # Split pid's in array
    pids = pids.split()
    if tkMessageBox.askyesno(appName, appname+" is currently open. \nClose and install new version?", icon='warning'):
      # Kill each PID of app
      for appProcess in pids :
        p1 = subprocess.Popen( 'kill -9 %s' % appProcess, shell=True, stdout=subprocess.PIPE )
        output = p1.communicate()[0] 
      return

    
def renderOfflineDialog():
    if tkMessageBox.showinfo(appName+" - Offline", "No Internet Connection \n\nConnect to the internet and try again.", icon='warning'):
      splashWindow.destroy()
      sys.exit()


def on_cancel_button_clicked(button):
    renderCancelDialog()  

    
def renderStartupSplash():
    global splashWindow
    global splashProgressBar
    global splashProgressPercent
    global splashLabel
    global splashLabelText
    # Create Main window
    splashWindow = Tk()
    splashWindow.title( appName+' '+appVersion )
    splashWindow.configure(background=defaultColor)
    splashWindow.resizable(FALSE,FALSE)
    splashWindow.geometry('305x350+0+0')
    
    # Center window
    x = (splashWindow.winfo_screenwidth() - splashWindow.winfo_reqwidth()) / 2
    y = (splashWindow.winfo_screenheight() - splashWindow.winfo_reqheight()) / 2
    splashWindow.geometry("+%d+%d" % (x-50, y-80))
 
    # Create an logo Image GIF only with PhotoImage
    logoImage = PhotoImage(file=iconPath)
    logoLabel = Label(image=logoImage)
    logoLabel.image = logoImage
    
    # Create progress bar
    splashProgressPercent = IntVar()
    splashProgressBar = Progressbar(splashWindow, orient=HORIZONTAL, length=280, mode='determinate')
    splashProgressBar['variable'] = splashProgressPercent

    # Set initial progress bar value 
    splashProgressBar.step(1)
    splashProgressPercent.set(10)
    
    # Create Text Label
    splashLabelText = StringVar()
    splashLabel = Label(splashWindow, textvariable=splashLabelText)
    splashLabelText.set('Initialising...')
    
    # a grid to attach the elements   
    logoLabel.grid(column=0, row=0)
    splashLabel.grid(column=0, row=1, columnspan=1)
    splashProgressBar.grid(column=0, row=2)

    # Show Window
    #splashWindow.mainloop()
    

def renderMainWindow():
    global headerLabelTxt
    global headerProgPercent
    global headerProgLabelTxt
    global itemProgressPercent
    global installButtonTxt
    global view
    global grid
    global cancelButton
    global installButton
    global mainWindow
    global checkItem
    global itemCheckBox
    global itemIcon
    global itemIconImage
    global frame

    # Create Main window   
    mainWindow = Tk()
    mainWindow.title( appName )
    mainWindow.configure(background=defaultColor)
    mainWindow.resizable(TRUE,TRUE)
    mainWindow.geometry('560x540+0+0')

    # Center the main window
    x = (mainWindow.winfo_screenwidth() - mainWindow.winfo_reqwidth()) / 2
    y = (mainWindow.winfo_screenheight() - mainWindow.winfo_reqheight()) / 2
    mainWindow.geometry("+%d+%d" % (x-180, y-175))
 
    # Create Top Frame
    topFrame = Frame(mainWindow)
    topFrame.pack( side = TOP )
     
    # Add Header to Top Frame
    headerLabelTxt = StringVar()
    headerLabel = Label(topFrame, textvariable = headerLabelTxt, justify=CENTER )
    headerLabelTxt.set('Select the software you would like to install')
    headerLabel.grid(row=0, column=0, columnspan=5, pady=10)
    
    headerProgPercent = IntVar()
    headerProgress = Progressbar(topFrame, length=495, orient=HORIZONTAL, mode='determinate')
    headerProgress['variable'] = headerProgPercent
    headerProgress.grid(row=1, column=0, columnspan=5)
    
    headerProgLabelTxt = StringVar()
    headerProgressLabel = Label(topFrame, textvariable = headerProgLabelTxt, foreground='#777777', justify=CENTER )
    headerProgLabelTxt.set('Click Install to Start')
    headerProgressLabel.grid(row=2, column=0, columnspan=5, pady=(0,10))

    headerSeparator = Separator(topFrame, orient='horizontal')
    #headerSeparator.grid(row=3, column=0, columnspan=5, pady=5, sticky='ew')
    headerSeparator.grid(row=3, column=0, columnspan=5, pady=5)
    
    # Bottom Frame
    bottomFrame = Frame(mainWindow)
    bottomFrame.pack( side = BOTTOM )
  
    copyrightLabel = Label(bottomFrame, text="List Date "+datestampConvert(localVersion), foreground='#666666', font=('default', 11, 'normal'), width=35, justify=LEFT, anchor=W )
    copyrightLabel.grid(row=0, column=0, columnspan=3, pady=10)
    
    cancelButton = Button(bottomFrame, text="Cancel", command=renderCancelDialog )
    cancelButton.grid(row=0, column=4, columnspan=1, pady=10, padx=5)
    
    installButtonTxt='Install'
    installButton = Button(bottomFrame, text=installButtonTxt, command=on_install_thread )
    installButton.grid(row=0, column=5, columnspan=1, pady=10, padx=5)
   
    # Middle Frame RENDER LAST
    # Call VerticalScrolledFrame to do the frame + grid + scrollbar magic
    frame = VerticalScrolledFrame(mainWindow)
    frame.pack(side="right", fill="y")

    # Build list display line for line as array append
    offset = 5
    checkItem = []
    itemCheckBox = []
    itemTitle = []
    itemVersion = []
    itemDescription = [] 
    itemProgressPercent = []
    itemProgress = []
    itemIconImage = []
    itemIcon = []
    
    # Add each item to 'frame.interior' NOT mainWindow for scrollbars
    for i in range(len(titleList)):
        checkItem.append(IntVar())
        itemCheckBox.append(Checkbutton(frame.interior, variable=checkItem[i], command=on_cell_toggle))
        itemTitle.append(Label(frame.interior, text=titleList[i], width=12, justify=LEFT ))
        itemVersion.append(Label(frame.interior, text=versionList[i], foreground='#AAAAAA', width=8, justify=CENTER, anchor=CENTER ))
        itemDescription.append(Label(frame.interior, text=descriptionList[i], foreground='#555555', width=20, justify=LEFT))
        itemProgressPercent.append(IntVar())
        itemProgress.append(Progressbar(frame.interior, orient=HORIZONTAL, length=150, mode='determinate'))
        itemProgress[i]['variable'] = itemProgressPercent[i]

        itemIconImage.append(PhotoImage(file=iconPathList[i]))
        itemIcon.append(Label(frame.interior, image=itemIconImage[i]))
        itemIcon[i].image = itemIconImage[i]
        
        # Set Checkbox depending on install state
        # must set value because IntVar object instance is created
        # must use checkItem[i].get to get current state
        checkItem[i].set(selectBox[i])
   
        # Add to layout
        itemCheckBox[i].grid(row=i+offset, column=0)
        itemTitle[i].grid(row=i+offset, column=1)
        itemVersion[i].grid(row=i+offset, column=2)
        itemDescription[i].grid(row=i+offset, column=3)
        itemProgress[i].grid(row=i+offset, column=4)
        itemIcon[i].grid(row=i+offset, column=5, padx=(5,10))
         
        refreshGui(mainWindow)
  
    # Main display rendered
    appendToLog('[Notice] Main display rendered')
    
    # End of Main Menu Render
    

def getText(nodelist):
    rc = []
    for node in nodelist:
        if node.nodeType == node.TEXT_NODE:
            rc.append(node.data)
    return ''.join(rc)
    
 
def checkSoftwareUpdate(localver, newver):
    # Determine which version is newer
    # Remove word 'Build' if present
    tempVerLocalPre = localver.replace('Build','').strip()
    tempVerListPre = newver.replace('Build','').strip()

    # Remove bit after space - assume version is first
    tempVerLocalPre = tempVerLocalPre.split(' ')[0]
    tempVerListPre = tempVerListPre.split(' ')[0]

    # Split . into array
    tempVerLocal = tempVerLocalPre.split('.')
    tempVerList = tempVerListPre.split('.')
    
    # Count array items
    tempVerLocalLen = len(tempVerLocal)         
    tempVerListLen = len(tempVerList)
    
    # Get version with least items to compare
    if tempVerLocalLen > tempVerListLen :
      verItems = tempVerListLen
    else: 
      verItems = tempVerLocalLen
     
    setUpdateItem = False
    
    try:
        while True :  
          for verNumItem in range(verItems):
            # Break if ordinal value higher than local
            if int(tempVerList[verNumItem]) > int(tempVerLocal[verNumItem]) :
              setUpdateItem = True
              break
            # Break if ordinal value less than local
            if int(tempVerList[verNumItem]) < int(tempVerLocal[verNumItem]) :
              break
          # break out of while loop when done checking each number  
          break
    except:
        debugPrint('[Warning] Cannot compare version numbers')
        appendToLog('[Warning] Cannot compare version numbers')

    return setUpdateItem

 
def parsePlistXml(url,searchkey):
    # Get value for plist xml using plistlib
    dom = plistlib.readPlist(url)
    try:
        searchkeyvalue = dom[searchkey]
    except:
        searchkeyvalue = ''
        
    return searchkeyvalue
    
        
def checkInstall(software):
    # Check if software .app is in subfolder and maybe folder has name like .localized as well
    fileExt = os.path.splitext(software)[1][1:]
    if fileExt != 'app':
      appPath = os.path.join(appsFolder, software, software+'.app')
      if '.localized.app' in appPath:
        appPath = appPath.replace('.localized.app', '.app')
    else:
      appPath = os.path.join(appsFolder, software)
   
    # Check each item and if one is missing assume not installed 
    if os.path.exists(appPath):
      isInstalled = True # true if it is installed
      # Check installed version of app
      try:       
        bashCommand="mdls -name kMDItemVersion %s | cut -d'\"' -f2" % appPath.replace(' ', '\ ')
        p1 = subprocess.Popen( bashCommand, shell=True, stdout=subprocess.PIPE )
        appInstVersion = p1.communicate()[0].strip()
        # If we cannot get local version from app file meta try other options
        if 'null' in appInstVersion :
          # Check Info.plist in app folder
          xmlPlistPath = os.path.join(appPath,'Contents', 'Info.plist')
          if os.path.exists(xmlPlistPath) :
              # check CFBundleShortVersionString key for version
              appInstVersion = parsePlistXml(xmlPlistPath, 'CFBundleShortVersionString')
              # check CFBundleVersion key for version
              if not appInstVersion :
                  appInstVersion = parsePlistXml(xmlPlistPath, 'CFBundleVersion')
                  if not appInstVersion :
                      raise
      except:
        debugPrint('[Warning] Cannot get installed version of %s' % appPath.replace(' ', '\ '))
        appendToLog('[Warning] Cannot get installed version of %s' % appPath.replace(' ', '\ '))
        appInstVersion = '0'        
    else:
      isInstalled = False
      appInstVersion = '0'      
        
    # if installed return true/false and app installed version       
    return (isInstalled, appInstVersion)


############################# Main Loop
#
if __name__ == "__main__":
  
  # Vars
  verboseDebug = False
 
  # Main Env Vars
  appName = 'Mac After Install'
  procName = 'mac-after-install'
  appVersion = '1.1 beta'
  userHome = os.getenv("HOME")
  timeStamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
  installDir = os.getcwd()
  appsFolder = '/Applications'
  logFile = '/var/log/mac-after-install.log'
  lockFilePath = os.path.join('/tmp/mac-after-install.lock')
  iconPath = os.path.join(installDir, 'mac-after-install.gif')
  iconPathError = os.path.join(installDir, 'lib', 'icons', 'red.gif')
  iconPathReinstall = os.path.join(installDir, 'lib', 'icons', 'orange.gif')
  iconPathOk = os.path.join(installDir, 'lib', 'icons', 'green.gif')
  iconPathBlank = os.path.join(installDir, 'lib', 'icons', 'dark-grey.gif')
  xmlFilename = 'mac-after-install.xml'
  xmlPath = os.path.join(installDir, xmlFilename)
  VersionFilename = 'version.txt'
  localVersion = 0
  localVersionPath = os.path.join(installDir, VersionFilename)
  remoteVersionDir = 'https://www.thefanclub.co.za/sites/default/files/mac-after-install/'
  remoteVersionPath = os.path.join(remoteVersionDir, VersionFilename)
  remoteXmlPath = os.path.join(remoteVersionDir, xmlFilename)
  localDownloads = '/tmp/mac-after-install_downloads'
  # App Vars
  connectionStatus = False
  installStatus = ''
  loop_thread = ''
  pulseTimer = 0
  timerAsync = 0
  progressTimer = 0
  p1 = ''
  defaultColor= '#E9E9E9'
  
  
  # Lock File
  try:
      lockFile = open(lockFilePath,'w')
      # Try to aquire lock
      fcntl.flock(lockFile, fcntl.LOCK_EX|fcntl.LOCK_NB)
      # File has not been locked before 
      fileIsLocked = False
  except:
      # File is already locked
      fileIsLocked = True

  if fileIsLocked: 
    sys.exit('[Notice] '+procName+' instance already running or you do not have admin rights to run the program.')

  lockFile.write('%d\n'%os.getpid())
  lockFile.flush()
  
  # Start Log file after use appendToLog
  writeToFile(logFile, ('['+timeStamp+'] '+appName+' '+appVersion+' - Started'+'\n'), 'w')
  debugPrint("[Notice] Log file created")
  appendToLog("[Notice] Log file created")
  
  # Get Dist Info
  (release, (verinfoa, verinfob, verinfoc), machine) = platform.mac_ver()
  debugPrint("Release : OS X %s" % release)
  appendToLog("Release : OS X %s" % release)
  debugPrint("Machine : %s" % machine)
  appendToLog("Machine : %s" % machine)
      
  # START Splash Screen
  renderStartupSplash()
  refreshGui(splashWindow)
  # need this to render splash screen at this point

  # Check if system is 64bit 
  if not machine == 'x86_64':
    renderPlatformDialog() 

  # Check internet connection
  splashLabelText.set('Checking internet connection...')
  splashProgressPercent.set(20)
  refreshGui(splashWindow)
  
  if checkInternetConnection('http://apple.com') == False:
      # OFFLINE
      renderOfflineDialog()
 
  # Check for list update 
  splashLabelText.set('Checking for updates...')
  splashProgressPercent.set(30)
  refreshGui(splashWindow)
  
  # Check for online updates of list
  checkListUpdate()

  # Parse the XML install file
  splashLabelText.set('Checking installed software...')
  splashProgressPercent.set(70)
  refreshGui(splashWindow)

  appendToLog('Parsing XML...')

  xmldoc = minidom.parse(xmlPath)

  # Declare arrays and get xml obj
  titleList = []
  xmlTitleListObj = xmldoc.getElementsByTagName('Title') 

  descriptionList = []
  xmlDescriptionListObj = xmldoc.getElementsByTagName('Description')
  
  appFileList = []
  xmlAppFileListObj = xmldoc.getElementsByTagName('AppFile')
  
  urlList = []
  xmlUrlListObj = xmldoc.getElementsByTagName('URL')
  
  versionList = []
  xmlVersionListObj = xmldoc.getElementsByTagName('Version')

  # Declare select box bool value array and progress
  selectBox = []
  progressBox = []
  installStateList = []
  iconPathList = []

  itemCount = len(xmlTitleListObj)
  item=0
  realCount = 0
  
  appendToLog('Building ListStore')

  # Copy xml obj values to build arrays for easy reference of each item
  # and build liststore for Gtk 
  for item in range(itemCount):

      # First item is the select box value
      # Check if software is installed here for each item before setting True
      # Also set progress to 100 if installed
      titleItem = getText(xmlTitleListObj[item].childNodes).strip()
      appFileItem = getText(xmlAppFileListObj[item].childNodes).strip()
      urlItem = getText(xmlUrlListObj[item].childNodes).strip()
      versionItem = getText(xmlVersionListObj[item].childNodes).strip()

      # Check if item is installed and installed version
      (installedItem, versionLocalItem) = checkInstall(appFileItem)
      if installedItem:
        # Check if software can be updated
        debugPrint("Installed : %s" % titleItem)
        appendToLog("Installed : %s" % titleItem)
        debugPrint("Version Local : [%s]" % str(versionLocalItem))
        appendToLog("Version Local : [%s]" % str(versionLocalItem))
        debugPrint("Version List  : [%s]" % str(versionItem))       
        appendToLog("Version List  : [%s]" % str(versionItem))
        
        updateItem = checkSoftwareUpdate(versionLocalItem, versionItem)

        debugPrint("Update : %s " % str(updateItem))        
        appendToLog("Update : %s " % str(updateItem))             
          
        # Set Checkbox and Icon
        if updateItem :
          selectBox.append(1)
          iconPathMod = iconPathReinstall
          debugPrint(titleItem+" update : "+ str(updateItem) )
          appendToLog(titleItem+" update : "+ str(updateItem) )
        else:
          selectBox.append(0)
          iconPathMod = iconPathOk
            
        progressValue = 0
        installStateList.append('installed')      
      else:
        selectBox.append(1)
        progressValue = 0
        iconPathMod = iconPathBlank
        installStateList.append('not-installed')
  
      # Build own arrays from xml 
      titleList.append(titleItem)
      descriptionList.append(getText(xmlDescriptionListObj[item].childNodes))
      appFileList.append(appFileItem)
      urlList.append(urlItem)
      versionList.append(versionItem)
      # Build Progress blank array
      progressBox.append(progressValue)
      # Build Icon Path mod array
      iconPathList.append(iconPathMod)
      
      # Build listStore select list array at the same time
      # using realCount to keep track of counters in the arrays 
      # because not all items are added the count goes out
      realCount = realCount + 1
      
  appendToLog('ListStore Created')
  
  splashLabelText.set('All Done')
  splashProgressPercent.set(100)
  refreshGui(splashWindow)
  
  # Splash mainloop never called so mainWindow.mainloop is the main GUI thread 
  # Kill Splash Screen
  splashWindow.destroy()
 
  # Render Main Window
  renderMainWindow()

  # Start Mainwindow loop  
  mainWindow.mainloop()

  # End
  sys.exit()
