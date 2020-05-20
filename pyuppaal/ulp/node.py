""" 
    Copyright (C) 2009 
    Andreas Engelbredt Dalsgaard <andreas.dalsgaard@gmail.com>
    Mads Chr. Olesen <mchro@cs.aau.dk>

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>. """

#AST
class Node:
    def __init__(self, type, children=[], leaf=[]):
        self.type = type
        self.children = children
        self.leaf = leaf

    def print_node(self):
        print "visit", "  "*self.level, self.type, 
        if self.leaf != []:
            print self.leaf
            if self.leaf.__class__.__name__ == 'Node':
                print "visit-node", "  "*(self.level+1), self.leaf.type
        else:
            print 
        return True

    def visit(self, visitor=None, level=0):
        """Visit this node and subnodes.
        visitor should be a function taking a node as parameter, and returning
        True if children should be visited."""
        self.level = level
        if not visitor:
            visitor = Node.print_node
        if visitor(self):
            for v in self.children:
                v.visit(visitor, self.level+1);


