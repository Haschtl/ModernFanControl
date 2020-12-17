using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Linq;
using System.Windows.Forms;


namespace RobvanderWoude
{
	static class RunHidden
	{
		static string progver = "1.00";

		[STAThread]
		static int Main( string[] args )
		{
			if ( args.Length == 0 || args[0] == "/?" )
			{
				return ShowHelp( );
			}
			if ( !File.Exists( args[0] ) && !Which( args[0] ) )
			{
				return ShowHelp( String.Format( "Invalid program file \"{0}\"", args[0] ) );
			}
			try
			{
				int rc = 0;
				using ( Process process = new Process( ) )
				{
					string commandline = Environment.CommandLine;
					string thisexec = Environment.GetCommandLineArgs( )[0];
					// Remove RunHidden.exe from command line
					if ( commandline.StartsWith( thisexec ) )
					{
						commandline = commandline.Substring( thisexec.Length ).Trim( );
					}
					else
					{
						// Assuming doublequotes
						commandline = commandline.Substring( thisexec.Length + 2 ).Trim( );
					}
					process.StartInfo.FileName = Environment.GetEnvironmentVariable( "COMSPEC" );
					process.StartInfo.Arguments = "/C " + commandline;
					process.StartInfo.UseShellExecute = false;
					process.StartInfo.RedirectStandardError = true;
					process.StartInfo.RedirectStandardInput = true;
					process.StartInfo.RedirectStandardOutput = true;
					process.StartInfo.WindowStyle = ProcessWindowStyle.Hidden;
					process.StartInfo.CreateNoWindow = true;
					process.Start( );
					process.WaitForExit( );
					rc = process.ExitCode;
				}
				return rc;
			}
			catch ( Exception e )
			{
				return ShowHelp( e.Message );
			}
		}


		static int ShowHelp( string errmsg = "" )
		{
			string helptext = String.Empty;
			if ( !String.IsNullOrWhiteSpace( errmsg ) )
			{
				helptext = String.Format( "ERROR:\t{0}\n\n\n", errmsg );
			}

			helptext += String.Format( "RunHidden.exe,  Version {0}\n", progver );
			helptext += "Run a console program or script hidden\n\n";
			helptext += "Usage:\tRUNHIDDEN.EXE  command  [ arguments ]\n\n";
			helptext += "Where:\tcommand \tis the console program or script to be run\n";
			helptext += "\targuments \tis/are the optional command line argument(s)\n";
			helptext += "\t                    \tfor command\n\n";
			helptext += "Notes:\tUnlike RunNHide.exe, RunHidden.exe will wait for the\n";
			helptext += "\tspecified command to exit, and pass on its \"errorlevel\".\n";
			helptext += "\tHowever, like RunNHide.exe, RunHidden.exe runs the specified\n";
			helptext += "\tcommand in a separate process, so the specified command won't\n";
			helptext += "\tbe able to change environment variables for its parent process.\n\n";
			helptext += String.Format( "\tThe specified command is started with {0} /C\n", Path.GetFileName( Environment.GetEnvironmentVariable( "COMSPEC" ) ).ToUpper( ) );
			helptext += "\tso besides a true executable you can also specify a script file\n";
			helptext += "\twhich will then be run by its default interpreter. There is no\n";
			helptext += "\tguarantee, however, that this interpreter will run hidden.\n\n";
			helptext += "\tRedirection symbols and parentheses in the command line\n";
			helptext += "\targuments must be escaped with carets, e.g.\n";
			helptext += "\tRUNHIDDEN DIR ^> dir.log\n";
			helptext += "\tBetter still: use a \"wrapper\" batch file with the unescaped code.\n\n";
			helptext += "\tRunHidden.exe returns \"errorlevel\" -1 in case of (command line)\n";
			helptext += "\terrors, otherwise the specified command's errorlevel is returned.\n\n";
			helptext += "Written by Rob van der Woude\n";
			helptext += "http://www.robvanderwoude.com";

			MessageBox.Show( helptext, "Help for RunHidden.exe " + progver );

			return -1;
		}


		static bool Which( string file )
		{
			// Insert current directory before PATH and remove empty entries
			string[] path = String.Format( "{0};{1}", Environment.CurrentDirectory, Environment.GetEnvironmentVariable( "PATH" ) ).Split( ";".ToCharArray( ), StringSplitOptions.RemoveEmptyEntries );
			// Unlike PATH, do NOT remove empty entries, we REQUIRE the first entry of PATHEXT to be empty
			string[] pathext = ( ";" + Environment.GetEnvironmentVariable( "PATHEXT" ).ToLower( ) ).Split( ';' );
			foreach ( string folder in path )
			{
				// We assume that PATH does NOT contain UNC paths
				string dir = ( folder + @"\" ).Replace( @"\\", @"\" );
				foreach ( string ext in pathext ) // first entry of pathext MUST be empty
				{
					{
						// The EXTERNAL program FILE to be searched MUST have an extension, either specified on the command line or one of the extensions listed in PATHEXT.
						if ( ( file + ext ).IndexOf( '.' ) > -1 )
						{
							if ( File.Exists( dir + file + ext ) )
							{
								return true;
							}
						}
					}
				}
			}
			return false;
		}
	}
}
