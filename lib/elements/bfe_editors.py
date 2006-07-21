# -*- coding: utf-8 -*-
## $Id$

## This file is part of CDS Invenio.
## Copyright (C) 2002, 2003, 2004, 2005 CERN.
##
## The CDSware is free software; you can redistribute it and/or
## modify it under the terms of the GNU General Public License as
## published by the Free Software Foundation; either version 2 of the
## License, or (at your option) any later version.
##
## The CDSware is distributed in the hope that it will be useful, but
## WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
## General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with CDSware; if not, write to the Free Software Foundation, Inc.,
## 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.

def format(bfo, limit, separator=' ; ',extension='[...]', print_links="yes"):
    """
    Prints the list of editors of a record.
    
    @param limit the maximum number of editors to display
    @param separator the separator between editors.
    @param extension a text printed if more editors than 'limit' exist
    @param print_links if yes, print the editors as HTML link to their publications
    """
    from urllib import quote
    from invenio.config import weburl
    from invenio import bibrecord
    
    authors = bibrecord.record_get_field_instances(bfo.get_record(), '100')
    
    editors = [author for author in authors if bibrecord.field_get_subfield_value(author, "e")=="ed." ]

    if print_links.lower() == "yes":
        editors = map(lambda x: '<a href="'+weburl+'/search.py?f=author&p='+ quote(x) +'">'+x+'</a>', editors)

    if limit.isdigit() and len(editors) > int(limit):
        return separator.join(editors[:int(limit)]) + extension

    elif len(editors) > 0:
        return separator.join(editors)