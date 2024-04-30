#!/usr/bin/perl -w

# This script is the main entry point to the HTML Output from the PHENIX Online
# monitoring. It is a CGI script, written in perl. It is heavily based on 
# Morten's JavaScript Tree Menu http://www.treemenu.com.
# (The only add-on here is that the menu is dynamically generated, 
# thanks to a "menu" ASCII file which is generated by the MakeHTML 
# methods of OnlMonDraw children).
#
# The main purpose is to *dynamically* generate some javascript and html pages 
# that will produce a tree menu on the left of the navigator window, in order
# to navigate through the html outputs of a given run, and/or to allow the 
# user to select a given run to be shown.
#
#------------------------------------------------------------------------------
# Usage(s) (for users)
# 
# mon.cgi?runselect=1
#   will (dynamically) generate a page where you can see the list of runs
#   for which html output is available
# 
# mon.cgi?runtype=xxx&runnumber=yyy
#   will (dynamically) generate a tree menu for run yyy (of type xxx), where
#   xxx is either eventdata, calibdata, junkdata or unknowndata. The latter
#   state is a temporary one, and should last only a few minutes/hours after
#   the run is taken (ideally, if we were sure to be able to reliably get
#   the run type from the db at html production time, there would be no such
#   state). The move from unknowndata to the 3 other categories is expected
#   to be handled by another script, possibly ran from a cronjob.
#
# mon.cgi?help=1
#   get some help about usage of this script.
#
#------------------------------------------------------------------------------
#
# Usage(s) (internal)
#
# mon.cgi?runtype=xxx&runnumber=yyy&menucode=1
#   generate the javascript code used to produce the tree menu layout for a 
#   given run.
#
#------------------------------------------------------------------------------
#
# Expected directory structure : see README file.
#
#------------------------------------------------------------------------------
#
# Output customization.
#
# The various html pages produced can have their look modified through
# a Cascading Style Sheet (variable $css below). Icons can be changed
# too (see print_code_2 subroutine below).
#
#------------------------------------------------------------------------------
#
# L. Aphecetche (aphecetc@in2p3.fr) Nov. 2003.
#

use File::Basename;
use File::Find;
use CGI;

use strict;

use CGI::Carp 'fatalsToBrowser';
$CGI::POST_MAX = 1024;  # max 1K posts
$CGI::DISABLE_UPLOADS = 1;  # no uploads

my $css = "mon.css";

my $q = new CGI;

print $q->header();

my $help = $q->param('help');

if ( defined $help ) {
  help();
  print $q->end_html;
  exit;
}

my $photo = $q->param('photo');

my $contacts = $q->param('contacts');

my $runnumber = $q->param('runnumber');

my $runselect = $q->param('runselect');

my $menucode = $q->param('menucode');

my $runtype = $q->param('runtype');

my $runrange = $q->param('runrange');

if ( defined $menucode && defined $runtype && defined $runnumber )
  {
    # Produces the javascript code
    menu_code($runnumber,$runtype);
    exit;
  }

if ( defined $runselect ) 
  {
    # Makes a HTML page to select a run
    select_run($runrange);
    exit;
  }

if ( defined $runnumber && defined $runtype )
  {
    # Main entry point to show a run.
    show_run($runnumber,$runtype);
    exit;
  }

if ( defined $contacts || $photo eq 'Hide faces' )
  {
    show_contacts(0);
    exit;
  }

if ( $photo eq 'Show faces' )
  {
    show_contacts(1);
    exit;
  }

help();

exit;

#_____________________________________________________________________________
#_____________________________________________________________________________
#_____________________________________________________________________________

#_____________________________________________________________________________
sub dirlist {

  my $dir = shift;
  my $runrange = shift;

  my $dirname = basename($dir);

  print "<h1 class=\"dir\">$dirname</h1>";

if (! -d $dir)
{
print "$dir does not exist\n";
}
  opendir DIR,$dir or die "couldn't open $dir : $!";

  my $first = 1;

  foreach my $file ( reverse sort readdir(DIR) )
    {
      if ($file=~/^run/) {
	my $runrangename = runrangeName($file);
	print "<a class=\"dir\" href=\"mon.cgi?runselect=1&runrange=$file\">$runrangename</a><br>\n";
	if ( (! defined $runrange) && $first == 1 ) 
	  {
	    $first = 0;
	    runlist("$dir/$file");
	  }
	if ( defined $runrange && $runrange eq $file ) {
	  runlist("$dir/$file");
	}
      }
    }

  closedir(DIR);
}

#_____________________________________________________________________________
sub html_doctype {

  my $type = shift;

  if ( $type eq "Frameset" ) 
    {
      return "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.01 Frameset//EN\" \"http://www.w3.org/TR/html4/frameset.dtd\">\n";
    }
  elsif ( $type eq "Strict" )
    {
      return "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.01//EN\" \"http://www.w3.org/TR/html4/strict.dtd\">\n";
    }
  elsif ( $type eq "Transitional" ) 
    {
      return "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.01 Transitional//EN\" \"http://www.w3.org/TR/html4/loose.dtd\">\n";
    }
  else
    {
      die "Unknown DOCTYPE $type";
    }
}

#_____________________________________________________________________________
sub include_script {
  my $name = shift;
  print "<script type=\"text/javascript\" src=\"$name\"></script>\n";
}

#_____________________________________________________________________________
sub help {

  print "<h2>Quick help for the ".$q->url()." script</h2><HR>";
  print "This script is intended to navigate Run4 Online Monitoring Results <BR>\n";
  print "...more help text needed here... <hr><BR>";
  print "User accessible usage:<ul>";
  print "<li>help=1 : this page";
  print "<li>runtype=type&amp;runnumber=integer : gets the results for a given run";
  print "<li>runselect=1 : enter run selection mode. Only most recent run ranges are fully expanded (expanded means you see the run numbers belonging to this run range). Other might be expanded by clicking on them.";
  print "<li>runselect=1&runrange=run_xxxxxxxxxx_yyyyyyyyyy : enter run selection mode and expands only the given run range.";
  print "<li>contacts=1 : names of the developpers";
  print "<li>contacts=1&photo=1 : names and faces of the developpers";
  print "</ul>";

  print "<hr>";
  print "<p>A small note on runtypes. You probably know/understand what eventdata (real stuff), calibdata (also real stuff in some sense ;-) ) or junkdata (test stuff only) means, but what about unknowndata ? Well, this is just a temporary measure, until we get a clean way of figuring out the runtype at the moment html generation is taking place. For the moment this information is not readily available, so we tag all runs as unknowndata. Do not bother too much about this, it will be fixed!";

  print "<hr>Other possible usage, but not for users (for the script itself)";
  print "<ul>";
  print "<li>runtype=type&amp;runnumber=integer&amp;menucode=1 : (not meant for users) : used to create the javascript code to output the menu (only valid within a definite frameset, not to be used directly from the url selection bar in the browser)";
  print "</ul";
  print "<HR>";  
}

#_____________________________________________________________________________
sub makemenucode {

  #
  # From the "menu" file, produced the javascript code
  # that will output a tree menu.
  #

  my $run = shift;
  my $runtype = shift;

  my $dir = rundir($run,$runtype);
  my $menudescription = "$dir/menu";

  print "<script type=\"text/javascript\">\n";

  print "runnumber=$runnumber;\n";

  my @list = readfile($menudescription);

  my %dirlist; # will contain the names of all the directories
  # found in menu file.

  foreach my $l ( @list ) 
    {
      my $pos = rindex($l,"/");
      $pos = rindex(substr($l,0,$pos),"/");
      my $dir = substr($l,0,$pos);
      my @parts = split "/",$dir;
      foreach ( @parts )
	{
	  # be sure that we have all levels at least once 
	  # (only once in fact as we use a hash list).
	  my $d = join "/",@parts;
	  $dirlist{$d}=1;
	  pop @parts;
	}
    }

  # Now loop on all the directories, and associate
  # entries in menu file to those directories, to produce
  # the makeOnlMenu javascript function.

  print "function makeOnlMenu(menu)\n";
  print "{\n";

  if ( scalar keys %dirlist == 0 ) {
      print "  menu.addItem(\"RUN NOT FOUND\",\"runnotfound.html\")\n";
    }
  else {
    foreach my $d ( sort keys %dirlist )
      {
	my $var = $d;
	$var =~ tr/\//_/;
	print "  var $var = null;\n";
	print "  $var = new MTMenu;\n";
	my @parts = split "/",$d;      
	my $n = $#parts;
	my $parent = join "_",@parts[0 .. $n-1];
	print "  $parent.addItem(\"$parts[$n]\");\n";
	foreach my $v ( @list )
	  {
	    my $p1 = rindex($v,"/");
	    my $p2 = rindex(substr($v,0,$p1),"/");
	    if ( substr($v,0,$p2) eq $d )
	      {
		my $name = substr($v,$p2+1,$p1-$p2-1);
		my $link = "$dir/".substr($v,$p1+1);
		print "  $var.addItem(\"$name\",\"$link\");\n";
	      }
	  }
	my $isMenuFullyExpanded = "false";
	print "  $parent.makeLastSubmenu($var,$isMenuFullyExpanded);\n";
      }
  }

#  print " menu.addItem(\"RunControl\",\"http://www.sphenix-intra.bnl.gov:7815/cgi-bin/run_details.py?run=$runnumber\",\"text\",\"See what runcontrol have to say about this run\",\"link.gif\");\n";
  print "}\n";
  print "</script>\n";
}

#_____________________________________________________________________________
sub menu_code {

  my $runnumber=shift;
  my $runtype=shift;

  print_code_1();

  makemenucode($runnumber,$runtype);

  print_code_2();
}

#_____________________________________________________________________________
sub print_code_1 {

  print html_doctype("Strict");
  print "<html><head>\n";
  print_copyright();
  print "<script type=\"text/javascript\">\n";
  print " // Framebuster script to relocate browser when MSIE bookmarks this\n";
  print "  // page instead of the parent frameset.  Set variable relocateURL to\n";
  print "  // the index document of your website (relative URLs are ok):\n";
  print "  var relocateURL = \"/\";\n";
  print "  if(parent.frames.length == 0) {\n";
  print "    if(document.images) {\n";
  print "      location.replace(relocateURL);\n";
  print "    } else {\n";
  print "      location = relocateURL;\n";
  print "    }\n";
  print "  }\n";
  print "</script>\n";

  include_script("mtmcode.js");
  include_script("mtmtrack.js");
}

#_____________________________________________________________________________
sub print_code_2 {

  print "<script type=\"text/javascript\">\n";
  # General setup 

  print "MTMSSHREF = \"$css\";\n";
  print "MTMLinkedSS = true;\n";
  print "MTMDefaultTarget = \"text\";\n";
  print "MTMRootIcon = \"menu_root.gif\";\n";
  print "MTMenuText = \"RUN \"+runnumber.toString();\n";

  # Icons setup

  print "var MTMIconList = null;\n";
  print "MTMIconList = new IconList();\n";
  print "MTMIconList.addIcon(new MTMIcon(\"menu_link_external.gif\", \"http://\", \"pre\"));\n";
  print "MTMIconList.addIcon(new MTMIcon(\"menu_link_com.gif\", \".gif\", \"post\"));\n";
  print "MTMIconList.addIcon(new MTMIcon(\"iconhelp1.gif\", \"help\", \"pre\"));\n";

  # Menu setup

  print "var menu = null;\n";
  print "menu = new MTMenu();\n";
  print "makeOnlMenu(menu);\n";

  print "menu.addItem(\"RunSelect\",\"mon.cgi?runselect=1\",\"text\",\"Go here to select a given run\",\"select.gif\");\n";
  print "menu.addItem(\"Contacts\",\"mon.cgi?contacts=1\",\"text\",\"The humans behind the code\",\"iconemail3.gif\");\n";

  print "menu.addItem(\"Help\",\"mon.cgi?help=1\",\"text\",\"Get some help here\",\"help.gif\");\n";
  # Closures
  print "</script></head>\n";
  print "<body class=\"menu\" onload=\"MTMStartMenu(true)\">\n";
  print "</body></html>\n";
}

#_____________________________________________________________________________
sub print_copyright {
  print "<!--\n";
  print "// This script is a part of:\n";
  print "// Morten's JavaScript Tree Menu\n";
  print "// version 2.3.2-macfriendly, dated 2002-06-10\n";
  print "// http://www.treemenu.com/\n";
  print "// Copyright (c) 2001-2002, Morten Wang & contributors\n";
  print "// All rights reserved.\n";
  print "// This software is released under the BSD License which should accompany\n";
  print "// it in the file \"COPYING\".  If you do not have this file you can access\n";
  print "// the license through the WWW at http://www.treemenu.com/license.txt\n\n";
  print "-->\n";
}

#_____________________________________________________________________________
sub print_start_1 {

  my $run = shift;

  print html_doctype("Frameset");
  print "<html>\n";
  print "<head>\n";
  print "<link rel=\"stylesheet\" href=\"$css\" type=\"text/css\">\n";
  print "<title>sPHENIX Online Monitoring HTML Output for Run $run</title>\n";

  print_copyright();

  include_script("mtmcode.js");
  include_script("mtmtrack.js");

  print "<script type=\"text/javascript\">\n\n";
  print "  var MTMUsableBrowser = false;\n";
  print "  // browser sniffing routine\n";
  print "  browserName = navigator.appName;\n";
  print "  browserVersion = parseInt(navigator.appVersion);\n";
  print "  if (browserName == \"Netscape\" && browserVersion >= 3) {\n";
  print "    MTMUsableBrowser = (navigator.userAgent.indexOf(\"Opera\") == -1) ? true : false;\n";
  print "  } else if (browserName == \"Microsoft Internet Explorer\" && browserVersion >= 4) {\n";
  print "    MTMUsableBrowser = true;\n";
  print "  } else if(browserName == \"Opera\" && browserVersion >= 5) {\n";
  print "    MTMUsableBrowser = true;\n";
  print "  }\n";
  print "  if ( !MTMUsableBrowser ) {\n";
  print "    document.write(\"<P>Cannot work with this browser. Sorry.\");\n";
  print "  }\n";
  print "</script>\n\n";
  print "</head>\n";

  print "<!-- frameset creation -->\n\n";
  my $heading_height = 70;

  print "<FRAMESET cols=\"*\" rows=\"$heading_height,*\">\n";
  print "  <FRAME marginwidth=\"0\" marginheight=\"0\" frameborder=\"0\" src=\"heading.html\" name=\"heading\" noresize scrolling=\"no\">\n";
}

#_____________________________________________________________________________
sub print_start_2 {

  my $run = shift;
  my $runtype = shift;

  print "  <FRAME marginwidth=\"5\" marginheight=\"5\" src=\"mon.cgi?runselect=1\" name=\"text\" noresize frameborder=\"0\">\n";

  print "  </FRAMESET>\n";

  my $link = rundir($run,$runtype);
  $link .= "/menu.html";

  print "  <NOFRAMES>\n";
  print "  <P>This document uses frames. If you don't have them, you may try";
  print "     the plain <A HREF=\"$link\">HTML menu</A>\n";
  print "  </NOFRAMES>\n";
  print "</FRAMESET>\n";

  print "</html>\n";
}

#_____________________________________________________________________________
sub readfile {

  my $file = shift;

  my @list;

  open FILE,$file or return @list;

  while (<FILE>)
    {
      chomp;
      if ( length $_ > 0 ) 
	{
	  push @list, "menu/$_";
	}
    }
  close FILE;

  return @list;
}

#_____________________________________________________________________________
sub rundir {
  # From the runtype and the runnumber, construct the directory name
  # where the menu and menu.html files are to be found.
  my $runnumber = shift;
  my $runtype = shift;
  my $range = runrange($runnumber);
  return "$runtype/$range/$runnumber";
}

#_____________________________________________________________________________
sub runlist {

  my $dir = shift;
  my $dirname = basename($dir);
  my $path = dirname($dir);

  opendir RDIR,$dir or die "couldn't open $dir : $!";

  my $n = 0;

  foreach my $run ( sort readdir(RDIR) )
    {
      if ( (!($run=~/^\./)) && int $run > 0 ) {
	print "<a href=\"", $q->url(-relative=>1), 
	  "?runnumber=$run&amp;runtype=$path\" target=\"_top\" class=\"$path\">",
	    $run,"</a>&nbsp;";
	++$n;
	if ( $n % 5 == 0 ) {
	  print "&nbsp;<br>\n";
	}
      }
    }

  closedir RDIR;

  if ( $n % 5 != 0 ) 
    {
      print "<BR>\n";
    }
}

#_____________________________________________________________________________
sub runrange {
  my $run = shift;
  my $start = int $run/1000;
  my $range = sprintf("run_%010d_%010d",$start*1000,($start+1)*1000);
  return $range;
}

#_____________________________________________________________________________
sub runrangeName {
  my $rr = shift;
  # From a $rr=run_XXXXXXXXXX_YYYYYYYYYY runrangedir, 
  # produces an easier to read
  # string

  my $n1 = int substr($rr,4,10);
  my $n2 = int substr($rr,15,10);

  return "$n1->$n2";
}

#_____________________________________________________________________________
sub select_run {

  my $runrange = shift;

  print html_doctype("Transitional");
  print "<html>\n<head>\n";
  print "<link rel=\"stylesheet\" href=\"mon.css\" type=\"text/css\">\n";
  print "<title>sPHENIX OnlMon HTML Output : Run Selection</title>\n";
  print "</head>\n<body class=\"runselect\">\n";

  print "<P>Please click on a run range below to expand it (by default the latest runs are expanded), and then click on a run number to browse it.\n";

  print "<table border=\"1\">\n";
  print "<tr valign=\"top\">\n";

  if (-d "beam")
  {
      print "<td>\n";
      dirlist("beam",$runrange);
      print "</td>\n";
  }
  if (-d "calib")
  {
      print "<td>\n";
      dirlist("calib",$runrange);
      print "</td>\n";
  }
  if (-d "cosmics")
  {
      print "<td>\n";
      dirlist("cosmics",$runrange);
      print "</td>\n";
  }
  if (-d "junk")
  {
      print "<td>\n";
      dirlist("junk",$runrange);
      print "</td>\n";
  }
  if (-d "led")
  {
      print "<td>\n";
      dirlist("led",$runrange);
      print "</td>\n";
  }
  if (-d "pulser")
  {
      print "<td>\n";
      dirlist("pulser",$runrange);
      print "</td>\n";
  }
  if (-d "unknowndata")
  {
      print "<td>\n";
      dirlist("unknowndata",$runrange);
      print "</td>\n";
  }
  print "</table>\n";

  print "</body>\n</html>\n";
}

#_____________________________________________________________________________
sub show_contacts {

    my $show_photo = shift;

    print html_doctype("Transitional");
    print "<html>\n<head>\n";
    print "<link rel=\"stylesheet\" href=\"mon.css\" type=\"text/css\">\n";
    print "<title>The humans behind the sPHENIX Online Monitoring</title>\n";
    print "</head>\n<body class=\"contacts\">\n";

    print "<P>The humans behind the sPHENIX Online Monitoring...<BR><HR>";

    my %list = (
	"Master of the beast, html" => {
	    name => "Chris Pinkenburg",
	    email => "pinkenburg\@bnl.gov",
	    photo => "pinkenburg_chris.jpg",
	},
	"MVTX" => {
	    name => "Jakub Kvapil",
	    email => "jakub.kvapil\@lanl.gov",
	    photo => "kvapil_jakub.jpg"
	},
	"INTT" => {
	    name => "Joseph Bertaux",
	    email => "jbertau\@purdue.edu",
	    photo => "bertaux_joseph.jpg"
	},
	"TPC" => {
	    name => "Charles Hughes",
	    email => "chughes2\@iastate.edu",
	    photo => "sphenix-logo-white-bg.png"
	},
	"TPOT" => {
	    name => "Hugo Pereira Da Costa",
	    email => "hugo.pereira-da-costa\@lanl.gov",
	    photo => "sphenix-logo-white-bg.png"
	},
	"CEMC" => {
	    name => "Vincent Andrieux",
	    email => "andrieux\@illinois.edu",
	    photo => "sphenix-logo-white-bg.png"
	},
	"HCAL" => {
	    name => "Shuhang Li",
	    email => "sl4859\@columbia.edu",
	    photo => "sphenix-logo-white-bg.png"
	},
	"MBD" => {
	    name => "Mickey Chiu",
	    email => "chiu\@bnl.gov",
	    photo => "chiu_mickey.jpg"
	},
	"SEPD" => {
	    name => "Ron Belmont",
	    email => "belmonrj\@gmail.com",
	    photo => "sphenix-logo-white-bg.png"
	},
	"ZDC" => {
	    name => "Ejiro Umaka",
	    email => "ejironaomiumaka\@gmail.com",
	    photo => "umaka_ejiro.jpg"
	},
	"DAQ" => {
	    name => "JaeBeom Park",
	    email => "jpark4\@bnl.gov",
	    photo => "sphenix-logo-white-bg.png"
	},
	"LL1" => {
	    name => "Daniel Lis",
	    email => "Daniel.Lis\@colorado.edu",
	    photo => "sphenix-logo-white-bg.png"
	},
	"Spin" => {
	    name => "Devon Loomis",
	    email => "dloom\@umich.edu",
	    photo => "sphenix-logo-white-bg.png"
	}
	);

    print "<table>\n";
    my $photodir = "./photos";

    foreach my $l ( sort keys %list )
    {
	my $d = \%{$list{$l}};
	my $component = $l;

	my @name = split ',',$$d{"name"};
	my @email = split ",", $$d{"email"};
	my @photo = split ",",$$d{"photo"};

	for ( my $i = 0; $i < $#name+1; ++$i ) {
	    my $name = $name[$i];
	    my $email = $email[$i];
	    my $photo = $photo[$i];
	    print "<TR><TD class=\"devcomponent\">$component",
	    "<td><A class=\"devmail\" HREF=\"mailto:$email\">$name</a>";
	    if ( $show_photo == 1 )
	    {
		print "<td><img src=\"$photodir/$photo\" width=\"115\" height=\"115\">\n";
	    }
	}
    }

    print "<tr><td>&nbsp;<td>";

    print $q->start_form("post");#,"./mon.cgi?contacts=1&photo=1");
    if ( $show_photo == 0 )
    {
	print $q->submit(-name=>'photo',-label=>'Show faces');
    }
    else
    {
	print $q->submit(-name=>'photo',-label=>'Hide faces');
    }
    print $q->endform();

    print "</table>\n";

    print "</body></html>\n";
}

#_____________________________________________________________________________
sub show_run {

  my $run = shift;
  my $runtype = shift;

  print_start_1($run,$runtype);

  my $menu_width = 250;
  print "  <FRAMESET cols=\"$menu_width,*\" rows=\"*\">\n";
  print "    <FRAMESET rows=\"0,*\">\n";
  my $codesrc = $q->url(-relative=>1)."?runnumber=$run&amp;menucode=1&amp;runtype=$runtype";

  print "      <FRAME marginwidth=\"0\" marginheight=\"0\" src=\"$codesrc\" name=\"code\" noresize scrolling=\"no\" frameborder=\"0\">\n";

  print "      <FRAME marginwidth=\"5\" marginheight=\"5\" src=\"menu_empty.html\" name=\"menu\" noresize scrolling=\"auto\" frameborder=\"0\">\n";

  print "    </FRAMESET>\n";

  print_start_2($run,$runtype);
}
