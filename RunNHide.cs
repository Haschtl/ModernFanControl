using System;
using System.Diagnostics;
using System.IO;
using System.Windows.Forms;


namespace RobvanderWoude
{
	static class RunNHide
	{
		static string progver = "1.01";
		static string currentdir = Directory.GetCurrentDirectory( );
		static string arguments = String.Empty;
		static int rc = 0;


		[STAThread]
		static int Main( string[] args )
		{
			if ( args.Length == 0 || args[0] == "/?" )
			{
				return ShowHelp( );
			}
			else
			{
				string exec = args[0];
				if ( args.Length > 1 )
				{
					string arguments = Environment.CommandLine;
					string thisexec = Environment.GetCommandLineArgs( )[0];
					// Remove RunNHide.exe from command line
					if ( arguments.StartsWith( thisexec ) )
					{
						arguments = arguments.Substring( thisexec.Length ).Trim( );
					}
					else
					{
						// Assuming doublequotes
						arguments = arguments.Substring( thisexec.Length + 2 ).Trim( );
					}
					// Remove specified program name from command line
					if ( arguments.StartsWith( exec ) )
					{
						arguments = arguments.Substring( exec.Length ).Trim( );
					}
					else
					{
						// Assuming doublequotes
						arguments = arguments.Substring( exec.Length + 2 ).Trim( );
					}
				}
				exec = GetFullPath( exec );
				try
				{
					ProcessStartInfo psi = new ProcessStartInfo( );
					if ( Path.GetExtension( exec ).ToLower( ) == ".exe" )
					{
						psi.FileName = exec;
						psi.Arguments = arguments;
					}
					else
					{
						psi.FileName = Environment.GetEnvironmentVariable( "COMSPEC" );
						psi.Arguments = String.Format( "/C START /B /MIN \"\" \"{0}\" {1}", exec, arguments );
					}
					psi.CreateNoWindow = true;
					psi.LoadUserProfile = false;
					psi.RedirectStandardError = false;
					psi.RedirectStandardOutput = false;
					psi.UseShellExecute = false;
					psi.WindowStyle = ProcessWindowStyle.Hidden;
					psi.WorkingDirectory = currentdir;
					Process process = new Process( );
					process.StartInfo = psi;
					process.Start( );
					return rc;
				}
				catch ( Exception e )
				{
					MessageBox.Show( e.ToString( ) );
					return ShowHelp( e.Message );
				}
			}
		}


		static string GetFullPath( string filename )
		{
			string fullpath = filename;
			bool execfound = false;
			if ( File.Exists( fullpath ) )
			{
				fullpath = Path.GetFullPath( fullpath );
				execfound = true;
			}
			else
			{
				string[] path = ( currentdir + ";" + Environment.GetEnvironmentVariable( "PATH" ) ).Split( ";".ToCharArray( ) );
				string[] pathext = ( ";" + Environment.GetEnvironmentVariable( "PATHEXT" ) ).Split( ";".ToCharArray( ) );
				if ( !execfound )
				{
					foreach ( string dir in path )
					{
						if ( !execfound )
						{
							foreach ( string ext in pathext )
							{
								if ( !execfound )
								{
									if ( File.Exists( Path.Combine( dir, fullpath + ext ) ) )
									{
										fullpath = Path.Combine( dir, fullpath + ext );
										execfound = true;
									}
								}
							}
						}
					}
				}
			}
			if ( !execfound ) // might be internal command or file association
			{
				arguments = String.Format( "/C START /B /MIN \"\" \"{0}\" {1}", fullpath, arguments );
				fullpath = Environment.GetEnvironmentVariable( "COMSPEC" );
				rc = 2;
			}
			return fullpath;
		}


		static int ShowHelp( params string[] args )
		{
			string title = "Help for RunNHide " + progver;
			string helptext = String.Empty;
			if ( args.Length > 0 )
			{
				helptext += String.Format( "ERROR:\t{0}\n\n", args );
				title = "RunNHide Error";
			}
			helptext += String.Format( "RunNHide,  Version {0}\n", progver );
			helptext += "Start a console program or script in a hidden window\n\n";
			helptext += "Usage:\tRUNNHIDE    command    [ arguments ]\n\n";
			helptext += "Where:\tcommand \tis the console program or script to be run\n";
			helptext += "\targuments \tis/are the optional command line\n";
			helptext += "\t                    \targument(s) for command\n\n";
			helptext += "Notes:\t\"command\" will be started in a separate process, so catching\n";
			helptext += "\terrors or the command's errorlevel, or changing environment\n";
			helptext += "\tvariables is not possible; run \"command\" in a \"wrapper\" batch\n";
			helptext += "\tfile to add your own cusom error handling.\n\n";
			helptext += "\tRedirection symbols and parentheses in the command line\n";
			helptext += "\targuments must be escaped with carets, e.g.\n\tRUNNHIDE DIR ^> dir.log\n";
			helptext += "\tBetter still: use a \"wrapper\" batch file with the unescaped code.\n\n";
			helptext += "\tIf \"command\" is a file with a registered file association, it will be\n";
			helptext += "\tstarted with the standard command interpreter:\n";
			helptext += String.Format( "\t{0} /C START /B /MIN \"command\" [ arguments ]\n", Path.GetFileName( Environment.GetEnvironmentVariable( "COMSPEC" ) ).ToUpper( ) );
			helptext += "\tThis will in turn start the file in its associated program; however,\n";
			helptext += "\tthere is no guarantee that the associated program will run hidden.\n\n";
			helptext += "\tIf \"command\" cannot be found in the PATH, not even after\n";
			helptext += "\tappending extension found in PATHEXT, RunNHide.exe will\n";
			helptext += "\ttry and start it using the standard command interpreter,\n";
			helptext += "\tlike it does for registered file types.\n\n";
			helptext += "\tRunNHide.exe will return errorlevel 1 in case of detected errors,\n";
			helptext += "\tor 2 if the command file could not be found, or 0 otherwise.\n\n";
			helptext += "Written by Rob van der Woude\nhttp://www.robvanderwoude.com";
			MessageBoxButtons button = MessageBoxButtons.OK;
			MessageBoxIcon icon = MessageBoxIcon.None;
			MessageBox.Show( helptext, title, button, icon );
			return 1;
		}
	}
}
