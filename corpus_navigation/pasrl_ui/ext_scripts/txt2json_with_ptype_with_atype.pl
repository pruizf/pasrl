#!/usr/bin/perl

## Convertit le fichier d'export .txt de Pablo en fixture json pour import django
## python manage.py loaddata file.json

use strict;
use warnings;
use Data::Dumper;

my $usage = "perl $0 file.txt > file.json\n";
die $usage unless @ARGV == 1;
die $usage unless -f $ARGV[0];

my $date = "2016-02-12"; # sera corrigé en sql
my $author = "IISD-ENB";

my %documents;
my %sentences;
my %actors;
my %predicates;
my %predicate_types;
my %actor_types;
my %points;
my %propositions;

my $actor_mention_id;
my $predicate_mention_id;
my $point_mention_id;
my $proposition_id;

my $doc_id;
my $sent_id;
my $sent_name;

print "[";


open(INPUT, "<$ARGV[0]") || die $!;
while(<INPUT>){
    # restreindre à enb en debut d ligne, sinon mtnt qu'on a des propositions
    # avec des acteurs génériques comme "COP-16" ça match ces chaines !!
    if($_ =~ /^(enb[^-]+)-([0-9]+)\t+(.+?)\t*$/){
	$doc_id = $1;
	$sent_name = $1 . "-" . $2;
	my $sent = $3;
	$sent =~ s/\"/\\\"/g;
	$documents{$doc_id} = scalar(keys(%documents)) + 1 unless exists($documents{$doc_id});
	$sent_id = scalar(keys(%sentences)) + 1;
	$sentences{$sent_id} = {"text" => $sent, "doc" => $documents{$doc_id}, "name" => $sent_name};

    }

    elsif($_ =~ /[a-z]+/){
    # split on ONE tab, otherwise EMPTY POINTS shift fields left and json is broken
	my @tmp = split(/\t/, $_);
	my $actor = $tmp[0];
	# fix data pbs
	$actor =~ s/^American_Samoa$/Samoa/g;
	$actor =~ s/^Azerbaijan_Democratic_Republic$/Azerbaijan/g;
	my $atype = $tmp[1];
	#print "type " . $atype;
	my $predicate = $tmp[2];
	my $ptype = $tmp[3];
	my $point = $tmp[4];
	my $pstart = $tmp[5];
	my $pend = $tmp[6];
	my $conf = $tmp[7];
	$point =~ s/\"/\\\"/g;
	$point =~ s/^\s*\n*$/NONE/;
	chomp($conf);

	$actor_mention_id++;
	$predicate_mention_id++;
	$point_mention_id++;

	push(@{ $actors{$actor} }, {"text"=>$actor, "id"=>$actor_mention_id,
	                            "atype"=>$atype});
	$actor_types{$actor} = $atype;

	push(@{ $predicates{$predicate} }, {"text"=>$predicate, "id"=>$predicate_mention_id,
	                                    "ptype"=>$ptype});
	$predicate_types{$predicate} = $ptype;

	push(@{ $points{$point} }, {"text"=>$point, "id"=>$point_mention_id,
	                            "start"=>$pstart, "end"=>$pend, "conf"=>$conf});

	$proposition_id++;
	print_proposition($predicate_mention_id, $actor_mention_id, $point_mention_id,
	                  $sent_id, $proposition_id, $conf);

    }

}
close INPUT;

#print Dumper %actors;

print_documents(\%documents);
print_sentences(\%sentences);
print_actors(\%actors);
print_predicates(\%predicates);
my $points = print_points(\%points);
$points = substr($points, 0, -2);
print $points;
print "]";

sub print_documents{
    my $ref_docs = shift;
    # trier pour mieux voir les différences entre versions
    foreach my $doc (sort keys %{ $ref_docs }){
	print "{\"fields\": {\"date\": \"$date\", \"name\": \"$doc\", \"author\": \"$author\"}, \"model\": \"ui.document\", \"pk\": $ref_docs->{$doc}},\n";
    }
}

sub print_sentences{
    my $ref_sentences = shift;
    foreach my $sent_id (sort keys %{ $ref_sentences }){
	print "{\"fields\": {\"name\": \"", $ref_sentences->{$sent_id}->{"name"}, "\", \"text\": \"", $ref_sentences->{$sent_id}->{"text"}, "\", \"document\": ", $ref_sentences->{$sent_id}->{"doc"}, "}, \"model\": \"ui.sentence\", \"pk\": \"$sent_id\"},\n";
    }
}

sub print_actors{
    my $ref_actors = shift;
    my $i = 1;
    foreach my $actor (sort keys %{ $ref_actors }){
	print "{\"fields\": {\"name\": \"", $actor, "\", \"atype\": \"", $actor_types{$actor}, "\"}, \"model\": \"ui.actor\", \"pk\": $i},\n";
	foreach my $mention (@{ $ref_actors->{$actor} }){
	    print "{\"fields\": {\"text\": \"", $mention->{"text"}, "\",\"actor\": ", $i, "}, \"model\": \"ui.actormention\", \"pk\": ", $mention->{"id"},"},\n";
	}
	$i++;
    }
}

sub print_predicates{
    my $ref_predicates = shift;
    my $i = 1;
    foreach my $predicate (sort keys %{ $ref_predicates }){
	print "{\"fields\": {\"name\": \"", $predicate, "\", \"ptype\": \"", $predicate_types{$predicate}, "\"}, \"model\": \"ui.predicate\", \"pk\": $i},\n";
	foreach my $mention (@{ $ref_predicates->{$predicate} }){
	    print "{\"fields\": {\"text\": \"", $mention->{"text"}, "\",\"predicate\": ", $i, "}, \"model\": \"ui.predicatemention\", \"pk\": ", $mention->{"id"},"},\n";
	}
	$i++;
    }
}

sub print_points{
    my $ref_points = shift;
    my $i = 1;
    my $res;
    foreach my $point (sort keys %{ $ref_points }){
	$res .= "{\"fields\": {\"name\": \"" . $point . "\"}, \"model\": \"ui.point\", \"pk\": $i},\n";
	foreach my $mention (@{ $ref_points->{$point} }){
	    $res .= "{\"fields\": {\"text\": \"" .
	              $mention->{"text"} .
	              "\", \"start\": " . $mention->{"start"} .
	              ", \"end\": " . $mention->{"end"} .
	              #", \"conf\": " . $mention->{"conf"} . ", \"point\": " . $i .
	              ", \"point\": " . $i .
	              "}, \"model\": \"ui.pointmention\", \"pk\": " .
	              $mention->{"id"} . "},\n";
	}
	$i++;
    }
    return $res;
}


sub print_proposition{
    my ($predicate_mention_id, $actor_mention_id, $point_mention_id, $sent_id, $proposition_id, $conf) = @_;

    print "{\"fields\": {\"predicateMention\": $predicate_mention_id, \"actorMention\": $actor_mention_id, \"pointMention\": $point_mention_id, \"sentence\": \"$sent_id\", \"conf\": $conf}, \"model\": \"ui.proposition\", \"pk\": $proposition_id},\n";
}
