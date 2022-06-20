# coding: utf-8
# Your code here!

#!/usr/bin/env python
'''
This script generates table seating assignments for SSP, trying to minimize the
number of repeat interactions between participants, achieve a reasonable gender
balance, and so on.

Put your data into the Configuration section, at top, to use with a new campus. 

(Written by Dougal Sutherland '06 for the Westmont campus in 2011.)
'''
# requires python 2.7
# if you really want to run it on an earlier version, just change the
# collections.Counter to a defaultdict(int), and change the dictionary
# comprehensions

from __future__ import division

import collections
import itertools
import math
import random

################################################################################
################################ Configuration #################################

# Set to False to print out in text, or a filename if you have python-docx.
USE_DOCX = 'dinner.docx'

# The number of weeks of tables to generate.
NUM_WEEKS = 6

# Note that people are inserted as "name/m" or "name/f", to mark gender.

# This dictionary has table names as keys, and values are tuples of names who
# are fixed at those tables. If for some reason there are more tables than
# faculty, put an empty tuple --- ie tuple() --- as the value.
FIXED_PEOPLE = {
    1: ("(Faculty1)/f",),
    2: ("(Faculty2)/f",),
    3: ("(Faculty3)/m",),
    4: ("(Faculty4)/m",),
    5: ("(Faculty5)/f",),
    6: ("(Faculty6)/m",),
    7: ("(Faculty7)/m",),
}

# The people who move between tables from week to week, ie students and
# in some years certain faculty.
# (The filter() and split() calls make it into a list of strings.)
ROAMERS = filter(None, '''
Sarim/m
Sabrina/f
Kyra/f
Savar/m
Sam/m
Fernanda/f
Srijan/m
Gabriele/m
Celine/f
Ryan F./m
Ryan E./m
Natalie/f
Lucy K./f
Navit/m
Arthur/m
JD/m
Josiah/m
Drew/m
Rohan/m
Antonio/m
Sonia/f
Lucy G./f
Ai-Dan/f
Sophie/f
Oliver/m
Calvin/m
Fer/f
Vicki/f
Dipakshi/f
Ria/f
Kai/m
Victoria/f
Nico/m
Vicky/f
Megan/f
Moer/f
'''.split('\n'))

################################################################################

# Really, this should be a binary integer programming problem. But those are
# NP-hard, and also there's no good pure-Python software out there to solve
# them.
#
# So instead we can follow this simpler greedy algorithm:
#  - For each week:
#     - Assign the fixed people to tables
#     - Choose a roamer at random 
#        - add them to the best non-full table
#          (the table with the least prior interactions + gender badness)
#     - Repeat until all roamers are assigned

# Here are some constants to adjust the behavior of the assignment process.

# A function that determines the badness score of a given number of prior 
# interactions. Nonlinearity is probably good, because 3 repeat interactions
# is much worse than 2.
interaction_badness = lambda count: count ** 1.5

# The amount to add to interactions between a fixed person and a roamer. (So
# if the boost is 2, it counts like 3 interactions between roamers.)
fixed_interaction_boost = 2

# The amount to penalize a matching based on its gender balance. 
gender_badness = lambda m, f: abs(m - f) * 1.5

# The amount by which old interactions degrade (multiplicatively) after a week.
interaction_degradation = .9


# Some random convenience functions.

def format_to_print(name):
    '''
    Returns a namestring formatted properly for printing in output.
    '''
    return name[:name.rindex('/')]

def get_gender(name):
    '''
    Returns the gender from a namestring.
    '''
    return name[name.rindex('/')+1:]


################################################################################
################################ Core Algorithm ################################

def match_score(roamer, table_members, past_interacts):
    '''
    Gives a badness score for seating the given roamer with the other members,
    based on previous interactions and gender balance.

    Arguments:
        roamer: a name string
        table_members: a list of name strings
        past_interacts: a collections.Counter that associates sorted pairs of
                        names to the number of times they've been at the same
                        table

    Returns:
        A floating-point badness score for the match. Lower is better.
    '''
    badness = 0

    # add interaction badnesses
    for member in table_members:
        pair = tuple(sorted([roamer, member]))
        badness += interaction_badness(past_interacts[pair])

    # add gender badness
    male = sum(1 for person in table_members if get_gender(person) == 'm')
    female = len(table_members) - male
    badness += gender_badness(male, female)

    return badness


def best_match(roamer, tables, past_interacts):
    '''
    Finds the best table for a given roamer to be seated at, based on previous
    interactions and gender balance.

    Arguments:
        roamer: a name string like "Joe Schmoe/m"
        tables: a dictionary of table name -> list of member names (with gender)
        past_interacts: a collections.Counter that associates sorted pairs of
                        names to the number of times they've been at the same
                        table

    Returns:
        The table name of the best match.
    '''
    goodness = lambda (name, membs): match_score(roamer, membs, past_interacts)
    return min(tables.iteritems(), key=goodness)[0]


def do_week(roamers, fixed_people, past_interacts):
    '''
    Builds up a week's table assignment.

    Arguments:
        roamers: a list of roamer name strings
        fixed_people: a dictionary of table name -> fixed people names
        past_interacts: a collections.Counter that associates sorted pairs of
                        names to the number of times they've been at the same
                        table
    
    Returns:
        A dictionary of table names to name string lists.
    '''
    # make data structures for this week's tables
    tables = {}
    for name, fixed in fixed_people.iteritems():
        tables[name] = list(fixed)

    # calculate the min, max sizes tables can be
    total_num = len(roamers) + sum(map(len, fixed_people.itervalues()))
    avg_size = total_num / len(fixed_people)
    min_size = int(math.floor(avg_size))
    max_size = int(math.ceil(avg_size))

    # add people to the tables in random order
    for roamer in random.sample(roamers, len(roamers)):
        # first fill up all tables to their minimum size
        needy_tables = { n: membs for n,membs in tables.iteritems()
                         if len(membs) < min_size }

        # if no tables are needy, fill up tables that aren't overfull
        if not needy_tables:
            needy_tables = { n: membs for n,membs in tables.iteritems()
                             if len(membs) < max_size }

        table = best_match(roamer, needy_tables, past_interacts)
        tables[table].append(roamer)

    return tables


def add_to_past_interacts(tables, counter, fixed_people):
    '''
    Adds a week's worth of interactions to the past_interacts counter.

    Arguments:
        tables: a dictionary of table names to members
        counter: a past_interacts counter
        fixed_people: a set of fixed people (so they can be avoided more
                      aggressively)

    Returns: nothing
    '''
    # make the old interactions degrade a bit over time
    for k, v in counter.iteritems():
        counter[k] = v * interaction_degradation

    # add the new interactions to the counter
    for table_membs in tables.itervalues():
        for pair in itertools.combinations(table_membs, 2):
            counter[pair] += 1
            # add a boost for the fixed people
            if fixed_people.intersection(pair):
                counter[pair] += fixed_interaction_boost


def do_assignments(roamers=ROAMERS,
                   fixed_people=FIXED_PEOPLE,
                   num_weeks=NUM_WEEKS,
                   past_interacts=None):
    '''
    Does a full summer's worth of table assignments.

    Arguments:
        roamers: a list of roamer name strings
        fixed_people: a dictionary of table name -> fixed people names
        num_weeks: the number of weeks to do assignments for
        past_interacts: a pre-existing past_interacts counter, or None

    Returns:
        A list of dictionaries of table names to name string lists.
    '''
    if past_interacts is None:
        past_interacts = collections.Counter()
    fixed_set = set(sum(FIXED_PEOPLE.itervalues(), tuple()))

    weeks = []
    for week_num in range(num_weeks):
        # do the assignments
        this_week = do_week(roamers, fixed_people, past_interacts)

        # update metadata
        weeks.append(this_week)
        add_to_past_interacts(this_week, past_interacts, fixed_set)

    return weeks


################################################################################
#################################### Output ####################################

def make_docx(weeks, filename="dinner.docx", preweeks=0):
    '''
    Make a nice .docx output, using the python-docx package.

    You can get python-docx from github.com/mikemaccana/python-docx, but it
    requires lxml and maybe PIL as well, which are each largish and require
    a C compiler. If you don't have it, use the text output below.

    Arguments:
        weeks: a list of dictionaries mapping table names to name string lists
        filename: the name to put the output in (default "dinner.docx")
        preweeks: the number of weeks to skip in numbering (default 0)
    '''
    import docx as d

    # initial setup
    relationships = d.relationshiplist()
    document = d.newdocument()
    docbody = document.xpath('/w:document/w:body', namespaces=d.nsprefixes)[0]

    # insert content
    for num, tables in enumerate(weeks):
        docbody.append(d.heading("Week %d" % (num+1+preweeks), 1))

        for name, membs in sorted(tables.iteritems()):
            docbody.append(d.paragraph(""))
            docbody.append(d.heading("Table %s" % name, 2))
            for memb in membs:
                docbody.append(d.paragraph(format_to_print(memb)))

        if num != len(weeks) - 1:
            docbody.append(d.pagebreak(type='page', orient='portrait'))


    # Create our properties, contenttypes, and other support files
    coreprops = d.coreproperties(title='SSP Dinner Table Assignments',
            creator="The SSP TAs",
            keywords=['SSP', 'tables'],
            subject='Assignments for dinner tables at SSP')
    wordrelationships = d.wordrelationships(relationships)

    # save it
    d.savedocx(document, coreprops, d.appproperties(), d.contenttypes(),
               d.websettings(), wordrelationships, filename)


def print_to_text(weeks, preweeks=0):
    '''
    Print output in a format appropriate for the console; you'll have to
    copy-paste into something else to print nicely.

    Arguments:
        weeks: a list of dictionaries mapping table names to name string lists
        preweeks: the number of weeks to skip in numbering (default 0)
    '''
    for i, tables in enumerate(weeks):
        print '\n'
        print '-' * 80
        print "Week %d" % (i+preweeks)

        for name, membs in sorted(tables.iteritems()):
            print '\n'
            print '*Table %s*' % name
            for memb in membs:
                print format_to_print(memb)


################################################################################
######################## Accounting for Old Interactions #######################

# In 2011, we used an old script for the first week and got bad tables.
# This section just accounts for them. Feel free to delete for future versions.
# Change the if-main section below to call main() in that case.

oldtables = map(lambda s: filter(None, s.split('\n')), [
'''
Sean M./m
Jane B./f
Ellen Z./f
Marissa S./f
Phong V./m
Marisa M./f
Anelisse P./f
''',
'''
Mary M./f
Katy P./f
Mireia I.C./f
Kennedy A./m
Billy C./m
Aneesa S./f
''',
'''
Dougal S./m
Angela Z./f
Jasmine M./f
Bridget N./f
Linna M./f
Stephany R./f
''',
'''
Becky R./f
Laksh B./m
Jahnavi K./f
Leyatt B./f
Bowen L./m
Milly W./f
''',
'''
Anna H./f
Eric G./m
Sourabh R./m
Jeremy H./m
Pratheek N./m
Ling G./f
''',
'''
Prof. Mason/m
Sam H./m
Ming Z./f
Ahsan M./m
David D./m
Pathik S./m
''',
'''
Dr. Faison/m
Lawrence L./m
Pato R./m
Carsten P./m
Jason L./m
Virup G./m'''])

oldtables = dict(zip(range(len(oldtables)), oldtables))


def main_with_past():
    # account for preexisting tables
    fixed_set = set(sum(FIXED_PEOPLE.itervalues(), tuple()))
    past = collections.Counter()
    add_to_past_interacts(oldtables, past, fixed_set)

    # call the real main function
    main(past, preweeks=1)


################################################################################
################################# Main Wrapper #################################

def main(past=None, preweeks=0):
    # do the actual generation
    weeks = do_assignments()

    # print it
    if USE_DOCX:
        try:
            make_docx(weeks, filename=USE_DOCX, preweeks=preweeks)
            return
        except ImportError:
            import sys
            print >>sys.stderr, "Can't import docx -- printing to console instead."
    
    print_to_text(weeks, preweeks=preweeks)

if __name__ == '__main__':
    main_with_past()