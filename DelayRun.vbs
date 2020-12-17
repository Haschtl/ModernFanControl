Option Explicit

Dim i, intDelay, strArguments, wshShell

' Check command line arguments
If WScript.Arguments.Count < 2           Then Syntax
If InStr( WScript.Arguments(0), "/" )    Then Syntax
If InStr( WScript.Arguments(0), "?" )    Then Syntax
If InStr( WScript.Arguments(1), "/" )    Then Syntax
If InStr( WScript.Arguments(1), "?" )    Then Syntax
If Not IsNumeric( WScript.Arguments(0) ) Then Syntax
If CInt( WScript.Arguments(0) ) <= 0     Then Syntax

' First command line argument is the delay in seconds
intDelay = 1000 * CInt( WScript.Arguments(0) )

' The second and following arguments make up the command
strArguments = """" & WScript.Arguments(1) & """"
If WScript.Arguments.Count > 2 Then
	For i = 2 To WScript.Arguments.Count - 1
		strArguments = Trim( strArguments & " " & WScript.Arguments(i) )
	Next
End If

' Wait for the specified number of seconds
WScript.Sleep intDelay

' Start the command/program
Set wshShell = CreateObject( "WScript.Shell" )
wshShell.Run strArguments, 1, False
Set wshShell = Nothing


Sub Syntax
	Dim strMsg
	strMsg = "DelayRun.vbs,  Version 1.02" _
	       & vbCrLf _
	       & "Start a command after a delay" _
	       & vbCrLf & vbCrLf _
	       & "Usage:  DELAYRUN.VBS  delay  some_command  [ some_arguments ]" _
	       & vbCrLf & vbCrLf _
	       & "Where:  ""delay""           is the delay in seconds" _
	       & vbCrLf _
	       & "        ""some_command""    is the command to be run after the delay" _
	       & vbCrLf _
	       & "        ""some_arguments""  are optional arguments for ""some_command""" _
	       & vbCrLf & vbCrLf _
	       & "Notes:  Use this script to prevent ""traffic jams"" in your Startup folder:" _
	       & vbCrLf _
	       & "        modify the command line for each shortcut in the Startup folder," _
	       & vbCrLf _
	       & "        using this script to start each shortcut with a different delay." _
	       & vbCrLf _
	       & "        You may have to convert double quotes to single ones in the third" _
	       & vbCrLf _
	       & "        and following arguments." _
	       & vbCrLf _
	       & "        The working directory for ""some_command"" is this script's own" _
	       & vbCrLf _
	       & "        working directory (not to be confused with its own location)." _
	       & vbCrLf & vbCrLf _
	       & "Written by Rob van der Woude" & vbCrLf _
	       & "http://www.robvanderwoude.com"
	WScript.Echo strMsg
	WScript.Quit 1
End Sub
