# -*- coding: utf-8 -*-
##
## $Id$
##
## This file is part of CDS Invenio.
## Copyright (C) 2002, 2003, 2004, 2005, 2006, 2007 CERN.
##
## CDS Invenio is free software; you can redistribute it and/or
## modify it under the terms of the GNU General Public License as
## published by the Free Software Foundation; either version 2 of the
## License, or (at your option) any later version.
##
## CDS Invenio is distributed in the hope that it will be useful, but
## WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
## General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with CDS Invenio; if not, write to the Free Software Foundation, Inc.,
## 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.

"""
bibformat_xslt_engine - Wrapper for an XSLT engine.

Some functions are registered in order to be used in XSL code:
  - creation_date(recID)
  - modification_date(recID)

Dependencies: Need one of the following XSLT processors:
              - libxml2 & libxslt
              - 4suite

Used by: bibformat_engine.py
"""

__revision__ = "$Id$"

import sys
import os

from invenio.config import \
     weburl
from invenio.bibformat_config import \
     CFG_BIBFORMAT_TEMPLATES_PATH
from invenio.bibformat_dblayer import \
     get_creation_date, \
     get_modification_date

# The namespace used for BibFormat function
CFG_BIBFORMAT_FUNCTION_NS = "http://cdsweb.cern.ch/bibformat/fn"

# Import one XSLT processor
#
# processor_type:
#       -1 : No processor found
#        0 : libxslt
#        1 : 4suite
processor_type = -1
try:
    # libxml2 & libxslt
    processor_type = 0
    import libxml2
    import libxslt
except ImportError:
    pass

if processor_type == -1:
    try:
        # 4suite
        processor_type = 1
        from Ft.Xml.Xslt import Processor
        from Ft.Xml import InputSource
        from xml.dom import Node
    except ImportError:
        pass

if processor_type == -1:
    # No XSLT processor found
    sys.stderr.write('No XSLT processor could be found.\n' \
                     'No output produced.\n')
    sys.exit(1)

##################################################################
# Support for 'creation_date' and 'modification_date' functions  #

def get_creation_date_libxslt(ctx, recID):
    """
    libxslt extension function:
    Bridge between BibFormat and XSL stylesheets.
    Returns record creation date.

    Can be used in that way in XSL stylesheet
    (provided xmlns:fn="http://cdsweb.cern.ch/bibformat/fn" has been declared):
    <xsl:value-of select="fn:creation_date(445)"/> where 445 is a recID

    if recID is string, value is converted to int
    if recID is Node, first child node (text node) is taken as value
    """
    try:
        if isinstance(recID, str):
            recID_int = int(recID)
        elif isinstance(recID, int):
            recID_int = recID
        else:
            recID_int = libxml2.xmlNode(_obj=recID[0]).children.content

        return get_creation_date(recID_int)
    except Exception, err:
        sys.stderr.write("Error during formatting function evaluation: " + \
                         str(err) + \
                         '\n')

        return ''

def get_creation_date_4suite(ctx, recID):
    """
    libxslt extension function:
    Bridge between BibFormat and XSL stylesheets.
    Returns record creation date.

    Can be used in that way in XSL stylesheet
    (provided xmlns:fn="http://cdsweb.cern.ch/bibformat/fn" has been declared):
    <xsl:value-of select="fn:creation_date(445)"/>

    if value is int, value is converted to string
    if value is Node, first child node (text node) is taken as value
    """
    try:
        if len(recID) > 0 and isinstance(recID[0], Node):
            recID_int = recID[0].firstChild.nodeValue
            if recID_int is None:
                return ''
        else:
            recID_int = int(recID_int)

        return get_creation_date(recID_int)
    except Exception, err:
        sys.stderr.write("Error during formatting function evaluation: " + \
                         str(err) + \
                         '\n')

        return ''

def get_modification_date_libxslt(ctx, recID):
    """
    libxslt extension function:
    Bridge between BibFormat and XSL stylesheets.
    Returns record modification date.

    Can be used in that way in XSL stylesheet
    (provided xmlns:fn="http://cdsweb.cern.ch/bibformat/fn" has been declared):
    <xsl:value-of select="fn:creation_date(445)"/> where 445 is a recID

    if recID is string, value is converted to int
    if recID is Node, first child node (text node) is taken as value
    """
    try:
        if isinstance(recID, str):
            recID_int = int(recID)
        elif isinstance(recID, int):
            recID_int = recID
        else:
            recID_int = libxml2.xmlNode(_obj=recID[0]).children.content

        return get_modification_date(recID_int)
    except Exception, err:
        sys.stderr.write("Error during formatting function evaluation: " + \
                         str(err) + \
                         '\n')

        return ''

def get_modification_date_4suite(ctx, recID):
    """
    libxslt extension function:
    Bridge between BibFormat and XSL stylesheets.
    Returns record modification date.

    Can be used in that way in XSL stylesheet
    (provided xmlns:fn="http://cdsweb.cern.ch/bibformat/fn" has been declared):
    <xsl:value-of select="fn:modification_date(445)"/>

    if value is int, value is converted to string
    if value is Node, first child node (text node) is taken as value
    """
    try:
        if len(recID) > 0 and isinstance(recID[0], Node):
            recID_int = recID[0].firstChild.nodeValue
            if recID_int is None:
                return ''
        else:
            recID_int = int(recID_int)

        return get_modification_date(recID_int)
    except Exception, err:
        sys.stderr.write("Error during formatting function evaluation: " + \
                         str(err) + \
                         '\n')

        return ''

# End of date-related functions                                  #
##################################################################

def format(xmltext, template_filename=None, template_source=None):
    """
    Processes an XML text according to a template, and returns the result.

    The template can be given either by name (or by path) or by source.
    If source is given, name is ignored.

    bibformat_xslt_engine will look for template_filename in standard directories
    for templates. If not found, template_filename will be assumed to be a path to
    a template. If none can be found, return None.

    @param xmltext The string representation of the XML to process
    @param template_filename The name of the template to use for the processing
    @param template_source The configuration describing the processing.
    @return the transformed XML text.
    """
    if processor_type == -1:
        # No XSLT processor found
        sys.stderr.write('No XSLT processor could be found.')
        sys.exit(1)

    # Retrieve template and read it
    if template_source:
        template = template_source
    elif template_filename:
        try:
            path_to_templates = (CFG_BIBFORMAT_TEMPLATES_PATH + os.sep +
                                 template_filename)
            if os.path.exists(path_to_templates):
                template = file(path_to_templates).read()
            elif os.path.exists(template_filename):
                template = file(template_filename).read()
            else:
                sys.stderr.write(template_filename +' does not exist.')
                return None
        except IOError:
            sys.stderr.write(template_filename +' could not be read.')
            return None
    else:
        sys.stderr.write(template_filename +' was not given.')
        return None

    result = ""
    if processor_type == 0:
        # libxml2 & libxslt

        # Register BibFormat functions for use in XSL
        libxslt.registerExtModuleFunction("creation_date",
                                          CFG_BIBFORMAT_FUNCTION_NS,
                                          get_creation_date_libxslt)
        libxslt.registerExtModuleFunction("modification_date",
                                          CFG_BIBFORMAT_FUNCTION_NS,
                                          get_modification_date_libxslt)

        # Load template and source
        template_xml = libxml2.parseDoc(template)
        processor = libxslt.parseStylesheetDoc(template_xml)
        source = libxml2.parseDoc(xmltext)

        # Transform
        result_object = processor.applyStylesheet(source, None)
        result = processor.saveResultToString(result_object)

        # Deallocate
        processor.freeStylesheet()
        source.freeDoc()
        result_object.freeDoc()

    elif processor_type == 1:
        # 4suite

        # Init
        processor = Processor.Processor()

        # Register BibFormat functions for use in XSL
        processor.registerExtensionFunction(CFG_BIBFORMAT_FUNCTION_NS,
                                            "creation_date",
                                            get_creation_date_4suite)
        processor.registerExtensionFunction(CFG_BIBFORMAT_FUNCTION_NS,
                                            "modification_date",
                                            get_modification_date_4suite)

        # Load template and source
        transform = InputSource.DefaultFactory.fromString(template,
                                                       uri=weburl)
        source = InputSource.DefaultFactory.fromString(xmltext,
                                                       uri=weburl)
        processor.appendStylesheet(transform)

        # Transform
        result = processor.run(source)
    else:
        sys.stderr.write("No XSLT processor could be found")

    return result

if __name__ == "__main__":
    pass
