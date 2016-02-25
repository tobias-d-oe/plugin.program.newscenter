#!/usr/bin/python
###########################################################################
#
#          FILE:  plugin.program.newscenter/starter.py
#
#        AUTHOR:  Tobias D. Oestreicher
#
#       LICENSE:  GPLv3 <http://www.gnu.org/licenses/gpl.txt>
#       VERSION:  0.0.1
#       CREATED:  13.02.2016
#
###########################################################################
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation; either version 3 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, see <http://www.gnu.org/licenses/>.
#
###########################################################################
#     CHANGELOG:  (13.02.2016) TDOe - First Publishing
###########################################################################

import os,sys,xbmc,xbmcgui,xbmcaddon


mdelay = 0
mdelay2 = 0
icon = xbmc.translatePath("special://home/addons/plugin.program.newscenter/icon.png")
addon       = xbmcaddon.Addon()
enableinfo  = addon.getSetting('enableinfo')
translation = addon.getLocalizedString
notifyheader= str(translation(30010))
notifytxt   = str(translation(30106))
refreshcontent = int(addon.getSetting('mdelay')) * 60
WINDOW = xbmcgui.Window( 10000 )

xbmc.log("NewsCenter: Starting with Contentrefresh (%s)" % (addon.getSetting('mdelay')))

if int(addon.getSetting('mdelay')) == 0:
    xbmc.log("Do not start NewsCenter Service, content refresh is 0")
    sys.exit()


if enableinfo == 'true':
    xbmc.executebuiltin('XBMC.Notification('+notifyheader+', '+notifytxt+' ,4000,'+icon+')')




class MyMonitor( xbmc.Monitor ):
    def __init__( self, *args, **kwargs ):
        xbmc.Monitor.__init__( self )

    def onSettingsChanged( self ):
        settings_initialize()


def settings_initialize():
    xbmc.log("NewsCenter: Settings changed")
    xbmc.executebuiltin('XBMC.RunScript(plugin.program.newscenter)')


#if enableinfo == 'true':
#    xbmc.executebuiltin('XBMC.Notification("NewsCenter" , "aktualisierung wird durchgefuehrt" ,4000,'+icon+')')


skinnermode = addon.getSetting('skinnermode')
if skinnermode == 'True':    
    shouldrun = WINDOW.getProperty( "LatestNews.Service" )
    if shouldrun == "active":
        if enableinfo == 'true':
            xbmc.executebuiltin('XBMC.Notification("NewsCenter" , "aktualisierung wird durchgefuehrt" ,4000,'+icon+')')
        xbmc.executebuiltin('XBMC.RunScript(plugin.program.newscenter)')
else:
    if enableinfo == 'true':
        xbmc.executebuiltin('XBMC.Notification("NewsCenter" , "aktualisierung wird durchgefuehrt" ,4000,'+icon+')')
    xbmc.executebuiltin('XBMC.RunScript(plugin.program.newscenter)')



if __name__ == '__main__':
    monitor = MyMonitor()
    while not monitor.abortRequested():
        # Sleep/wait for abort for $refreshcontent seconds
        if monitor.waitForAbort(float(refreshcontent)):
            # Abort was requested while waiting. We should exit
            break
        skinnermode = addon.getSetting('skinnermode')
        if skinnermode == 'True':
            shouldrun = WINDOW.getProperty( "LatestNews.Service" )
            if shouldrun == "active":
                if enableinfo == 'true':
                    xbmc.executebuiltin('XBMC.Notification("NewsCenter" , "aktualisierung wird durchgefuehrt" ,4000,'+icon+')')
                xbmc.executebuiltin('XBMC.RunScript(plugin.program.newscenter)')
        else:
            if enableinfo == 'true':
                xbmc.executebuiltin('XBMC.Notification("NewsCenter" , "aktualisierung wird durchgefuehrt" ,4000,'+icon+')')
            xbmc.executebuiltin('XBMC.RunScript(plugin.program.newscenter)')
 


