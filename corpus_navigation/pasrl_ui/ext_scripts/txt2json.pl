#!/usr/bin/perl

## Convertit le fichier d'export .txt de Pablo en fixture json pour import django
## python manage.py loaddata file.json

use strict;
use warnings;
use Data::Dumper;

my $usage = "perl $0 file.txt > file.json\n";
die $usage unless @ARGV == 1;
die $usage unless -f $ARGV[0];

my $date = "2015-11-05";
my $author = "Pablo Ruiz";

my %documents;
my %sentences;
my %actors;
my %predicates;
my %points;
my %propositions;

my $actor_mention_id;
my $predicate_mention_id;
my $point_mention_id;
my $proposition_id;


my $doc_id;
my $sent_id;

print "[";


open(INPUT, "<$ARGV[0]") || die $!;
while(<INPUT>){
    if($_ =~ /([^-]+)-([0-9]+)\t+(.+?)\t*$/){
	$doc_id = $1;
	$sent_id = $2;
	my $sent = $3;
	$sent =~ s/\"/\\\"/g;
	$documents{$doc_id} = scalar(keys(%documents)) + 1 unless exists($documents{$doc_id});
	$sentences{$sent_id} = {"text" => $sent, "doc" => $documents{$doc_id}};
	
    }

    elsif($_ =~ /[a-z]+/){
	my @tmp = split(/\t+/, $_);
	my $actor = $tmp[0];
	my $predicate = $tmp[1];
	my $point = $tmp[2];
	$point =~ s/\"/\\\"/g;
	$point =~ s/^\s*\n*$/NONE/;
	chomp $point;

	
	$actor_mention_id++;
	$predicate_mention_id++;
	$point_mention_id++;

	push(@{ $actors{$actor} }, {"text"=>$actor, "id"=>$actor_mention_id});
	push(@{ $predicates{$predicate} }, {"text"=>$predicate, "id"=>$predicate_mention_id});
	push(@{ $points{$point} }, {"text"=>$point, "id"=>$point_mention_id});

	$proposition_id++;
	print_proposition($predicate_mention_id, $actor_mention_id, $point_mention_id, $sent_id, $proposition_id);
	
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
    foreach my $doc (keys %{ $ref_docs }){
	print "{\"fields\": {\"date\": \"$date\", \"name\": \"$doc\", \"author\": \"$author\"}, \"model\": \"ui.document\", \"pk\": $ref_docs->{$doc}},\n"; 
    }
}

sub print_sentences{
    my $ref_sentences = shift;
    foreach my $sent_id (keys %{ $ref_sentences }){
	print "{\"fields\": {\"text\": \"", $ref_sentences->{$sent_id}->{"text"}, "\", \"document\": ", $ref_sentences->{$sent_id}->{"doc"}, "}, \"model\": \"ui.sentence\", \"pk\": $sent_id},\n"; 
    }
}

sub print_actors{
    my $ref_actors = shift;
    my $i = 1;
    foreach my $actor (keys %{ $ref_actors }){
	print "{\"fields\": {\"name\": \"", $actor, "\"}, \"model\": \"ui.actor\", \"pk\": $i},\n";
	foreach my $mention (@{ $ref_actors->{$actor} }){
	    print "{\"fields\": {\"text\": \"", $mention->{"text"}, "\",\"actor\": ", $i, "}, \"model\": \"ui.actormention\", \"pk\": ", $mention->{"id"},"},\n";
	}
	$i++;
    }
}

sub print_predicates{
    my $ref_predicates = shift;
    my $i = 1;
    foreach my $predicate (keys %{ $ref_predicates }){
	print "{\"fields\": {\"name\": \"", $predicate, "\"}, \"model\": \"ui.predicate\", \"pk\": $i},\n";
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
    foreach my $point (keys %{ $ref_points }){
	$res .= "{\"fields\": {\"name\": \"" . $point . "\"}, \"model\": \"ui.point\", \"pk\": $i},\n";
	foreach my $mention (@{ $ref_points->{$point} }){
	    $res .= "{\"fields\": {\"text\": \"" . $mention->{"text"} . "\",\"point\": " . $i . "}, \"model\": \"ui.pointmention\", \"pk\": " .  $mention->{"id"} . "},\n";
	}
	$i++;
    }
    return $res;
}


sub print_proposition{
    my ($predicate_mention_id, $actor_mention_id, $point_mention_id, $sent_id, $proposition_id) = @_;

    print "{\"fields\": {\"predicateMention\": $predicate_mention_id, \"actorMention\": $actor_mention_id, \"pointMention\": $point_mention_id, \"sentence\": $sent_id}, \"model\": \"ui.proposition\", \"pk\": $proposition_id},\n"; 
}
