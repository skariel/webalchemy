

class Stacker:
    '''Allow stacking element creation with "with" statements
    
    eg.
    s = Stacker(self.rdoc.body)
    with s.stack('div', cls='panel') as panel:
        s.stack('div', text='Hello', cls='panel-heading')
        with s.stack('div', cls='panel-body'):
            s.stack(p="this is text inside body")
        s.stack('div', text="panel footer here", cls="panel-footer")
    '''
    def __init__(self, element, prev_stacker=None):
        # proxy everything to element - copy __dict__ and __class__
        self.__class__ = type(element.__class__.__name__,
                              (self.__class__, element.__class__),
                              {})
        self.__dict__ = element.__dict__

        if prev_stacker:
            self._stack = prev_stacker._stack
        else:
            self._stack = [element]
        self._element = element

        
    def stack(self, *args, **kwargs):
        '''Create an element - parent is head of stack'''
        parent = self._stack[-1]
        e = parent.element(*args, **kwargs)
        se = Stacker(e, self)
        return se
         
    def __enter__(self, **kwargs):
        self._stack.append(self._element)
        return self
    
    def __exit__(self, type, value, traceback):
        self._stack.pop()
        
        
    ###############################################################################    
    # "Shortcut" methods for element types
    
    # Sections

    def section(self, *args, **kwargs):
        '''
          The section element represents a generic section of a document or
          application. A section, in this context, is a thematic grouping of content,
          typically with a heading.
        '''
        return self.stack(typ="section", *args, **kwargs)

    def nav(self, *args, **kwargs):
        '''
      The nav element represents a section of a page that links to other pages or
      to parts within the page: a section with navigation links.
      '''
        return self.stack(typ="nav", *args, **kwargs)
    
    def article(self, *args, **kwargs):
        '''
      The article element represents a self-contained composition in a document,
      page, application, or site and that is, in principle, independently
      distributable or reusable, e.g. in syndication. This could be a forum post, a
      magazine or newspaper article, a blog entry, a user-submitted comment, an
      interactive widget or gadget, or any other independent item of content.
      '''
        return self.stack(typ="article", *args, **kwargs)
    
    def aside(self, *args, **kwargs):
        '''
      The aside element represents a section of a page that consists of content
      that is tangentially related to the content around the aside element, and
      which could be considered separate from that content. Such sections are
      often represented as sidebars in printed typography.
      '''
        return self.stack(typ="aside", *args, **kwargs)
    
    def h1(self, *args, **kwargs):
        '''
      Represents the highest ranking heading.
      '''
        return self.stack(typ="h1", *args, **kwargs)
    
    def h2(self, *args, **kwargs):
        '''
      Represents the second-highest ranking heading.
      '''
        return self.stack(typ="h2", *args, **kwargs)
    
    def h3(self, *args, **kwargs):
        '''
      Represents the third-highest ranking heading.
      '''
        return self.stack(typ="h3", *args, **kwargs)
    
    def h4(self, *args, **kwargs):
        '''
      Represents the fourth-highest ranking heading.
      '''
        return self.stack(typ="h4", *args, **kwargs)
    
    def h5(self, *args, **kwargs):
        '''
      Represents the fifth-highest ranking heading.
      '''
        return self.stack(typ="h5", *args, **kwargs)
    
    def h6(self, *args, **kwargs):
        '''
      Represents the sixth-highest ranking heading.
      '''
        return self.stack(typ="h6", *args, **kwargs)
    
    def hgroup(self, *args, **kwargs):
        '''
      The hgroup element represents the heading of a section. The element is used
      to group a set of h1-h6 elements when the heading has multiple levels, such
      as subheadings, alternative titles, or taglines.
      '''
        return self.stack(typ="hgroup", *args, **kwargs)
    
    def header(self, *args, **kwargs):
        '''
      The header element represents a group of introductory or navigational aids.
      '''
        return self.stack(typ="header", *args, **kwargs)
    
    def footer(self, *args, **kwargs):
        '''
      The footer element represents a footer for its nearest ancestor sectioning
      content or sectioning root element. A footer typically contains information
      about its section such as who wrote it, links to related documents,
      copyright data, and the like.
      '''
        return self.stack(typ="footer", *args, **kwargs)
    
    def address(self, *args, **kwargs):
        '''
      The address element represents the contact information for its nearest
      article or body element ancestor. If that is the body element, then the
      contact information applies to the document as a whole.
      '''
        return self.stack(typ="address", *args, **kwargs)
    
    
    # Grouping content
    
    def p(self, *args, **kwargs):
        '''
      The p element represents a paragraph.
      '''
        return self.stack(typ="p", *args, **kwargs)
    
    def hr(self, *args, **kwargs):
        '''
      The hr element represents a paragraph-level thematic break, e.g. a scene
      change in a story, or a transition to another topic within a section of a
      reference book.
      '''
        kwargs["is_single"] = True # TODO
        return self.stack(typ="hr", *args, **kwargs)
    
    def pre(self, *args, **kwargs):
        '''
      The pre element represents a block of preformatted text, in which structure
      is represented by typographic conventions rather than by elements.
      '''
        kwargs["is_pretty"] = False
        return self.stack(typ="pre", *args, **kwargs)
    
    def blockquote(self, *args, **kwargs):
        '''
      The blockquote element represents a section that is quoted from another
      source.
      '''
        return self.stack(typ="blockquote", *args, **kwargs)
    
    def ol(self, *args, **kwargs):
        '''
      The ol element represents a list of items, where the items have been
      intentionally ordered, such that changing the order would change the
      meaning of the document.
      '''
        return self.stack(typ="ol", *args, **kwargs)
    
    def ul(self, *args, **kwargs):
        '''
      The ul element represents a list of items, where the order of the items is
      not important - that is, where changing the order would not materially change
      the meaning of the document.
      '''
        return self.stack(typ="ul", *args, **kwargs)
    
    def li(self, *args, **kwargs):
        '''
      The li element represents a list item. If its parent element is an ol, ul, or
      menu element, then the element is an item of the parent element's list, as
      defined for those elements. Otherwise, the list item has no defined
      list-related relationship to any other li element.
      '''
        return self.stack(typ="li", *args, **kwargs)
    
    def dl(self, *args, **kwargs):
        '''
      The dl element represents an association list consisting of zero or more
      name-value groups (a description list). Each group must consist of one or
      more names (dt elements) followed by one or more values (dd elements).
      Within a single dl element, there should not be more than one dt element for
      each name.
      '''
        return self.stack(typ="dl", *args, **kwargs)
    
    def dt(self, *args, **kwargs):
        '''
      The dt element represents the term, or name, part of a term-description group
      in a description list (dl element).
      '''
        return self.stack(typ="dt", *args, **kwargs)
    
    def dd(self, *args, **kwargs):
        '''
      The dd element represents the description, definition, or value, part of a
      term-description group in a description list (dl element).
      '''
        return self.stack(typ="dd", *args, **kwargs)
    
    def figure(self, *args, **kwargs):
        '''
      The figure element represents some flow content, optionally with a caption,
      that is self-contained and is typically referenced as a single unit from the
      main flow of the document.
      '''
        return self.stack(typ="figure", *args, **kwargs)
    
    def figcaption(self, *args, **kwargs):
        '''
      The figcaption element represents a caption or legend for the rest of the
      contents of the figcaption element's parent figure element, if any.
      '''
        return self.stack(typ="figcaption", *args, **kwargs)
    
    def div(self, *args, **kwargs):
        '''
      The div element has no special meaning at all. It represents its children. It
      can be used with the class, lang, and title attributes to mark up semantics
      common to a group of consecutive elements.
      '''
        return self.stack(typ="div", *args, **kwargs)
    
    
    
    # Text semantics
    
    def a(self, *args, **kwargs):
        '''
      If the a element has an href attribute, then it represents a hyperlink (a
      hypertext anchor).
    
      If the a element has no href attribute, then the element represents a
      placeholder for where a link might otherwise have been placed, if it had been
      relevant.
      '''
        return self.stack(typ="a", *args, **kwargs)
    
    def em(self, *args, **kwargs):
        '''
      The em element represents stress emphasis of its contents.
      '''
        return self.stack(typ="em", *args, **kwargs)
    
    def strong(self, *args, **kwargs):
        '''
      The strong element represents strong importance for its contents.
      '''
        return self.stack(typ="strong", *args, **kwargs)
    
    def small(self, *args, **kwargs):
        '''
      The small element represents side comments such as small print.
      '''
        return self.stack(typ="small", *args, **kwargs)
    
    def s(self, *args, **kwargs):
        '''
      The s element represents contents that are no longer accurate or no longer
      relevant.
      '''
        return self.stack(typ="s", *args, **kwargs)
    
    def cite(self, *args, **kwargs):
        '''
      The cite element represents the title of a work (e.g. a book, a paper, an
      essay, a poem, a score, a song, a script, a film, a TV show, a game, a
      sculpture, a painting, a theatre production, a play, an opera, a musical, an
      exhibition, a legal case report, etc). This can be a work that is being
      quoted or referenced in detail (i.e. a citation), or it can just be a work
      that is mentioned in passing.
      '''
        return self.stack(typ="cite", *args, **kwargs)
    
    def q(self, *args, **kwargs):
        '''
      The q element represents some phrasing content quoted from another source.
      '''
        return self.stack(typ="q", *args, **kwargs)
    
    def dfn(self, *args, **kwargs):
        '''
      The dfn element represents the defining instance of a term. The paragraph,
      description list group, or section that is the nearest ancestor of the dfn
      element must also contain the definition(s) for the term given by the dfn
      element.
      '''
        return self.stack(typ="dfn", *args, **kwargs)
    
    def abbr(self, *args, **kwargs):
        '''
      The abbr element represents an abbreviation or acronym, optionally with its
      expansion. The title attribute may be used to provide an expansion of the
      abbreviation. The attribute, if specified, must contain an expansion of the
      abbreviation, and nothing else.
      '''
        return self.stack(typ="abbr", *args, **kwargs)
    
    def time_(self, *args, **kwargs):
        '''
      The time element represents either a time on a 24 hour clock, or a precise
      date in the proleptic Gregorian calendar, optionally with a time and a
      time-zone offset.
      '''
        return self.stack(typ="time_", *args, **kwargs)
    _time = time_
    
    def code(self, *args, **kwargs):
        '''
      The code element represents a fragment of computer code. This could be an XML
      element name, a filename, a computer program, or any other string that a
      computer would recognize.
      '''
        return self.stack(typ="code", *args, **kwargs)
    
    def var(self, *args, **kwargs):
        '''
      The var element represents a variable. This could be an actual variable in a
      mathematical expression or programming context, an identifier representing a
      constant, a function parameter, or just be a term used as a placeholder in
      prose.
      '''
        return self.stack(typ="var", *args, **kwargs)
    
    def samp(self, *args, **kwargs):
        '''
      The samp element represents (sample) output from a program or computing
      system.
      '''
        return self.stack(typ="samp", *args, **kwargs)
    
    def kbd(self, *args, **kwargs):
        '''
      The kbd element represents user input (typically keyboard input, although it
      may also be used to represent other input, such as voice commands).
      '''
        return self.stack(typ="kbd", *args, **kwargs)
    
    def sub(self, *args, **kwargs):
        '''
      The sub element represents a subscript.
      '''
        return self.stack(typ="sub", *args, **kwargs)
    
    def sup(self, *args, **kwargs):
        '''
      The sup element represents a superscript.
      '''
        return self.stack(typ="sup", *args, **kwargs)
    
    def i(self, *args, **kwargs):
        '''
      The i element represents a span of text in an alternate voice or mood, or
      otherwise offset from the normal prose in a manner indicating a different
      quality of text, such as a taxonomic designation, a technical term, an
      idiomatic phrase from another language, a thought, or a ship name in Western
      texts.
      '''
        return self.stack(typ="i", *args, **kwargs)
    
    def b(self, *args, **kwargs):
        '''
      The b element represents a span of text to which attention is being drawn for
      utilitarian purposes without conveying any extra importance and with no
      implication of an alternate voice or mood, such as key words in a document
      abstract, product names in a review, actionable words in interactive
      text-driven software, or an article lede.
      '''
        return self.stack(typ="b", *args, **kwargs)
    
    def u(self, *args, **kwargs):
        '''
      The u element represents a span of text with an unarticulated, though
      explicitly rendered, non-textual annotation, such as labeling the text as
      being a proper name in Chinese text (a Chinese proper name mark), or
      labeling the text as being misspelt.
      '''
        return self.stack(typ="u", *args, **kwargs)
    
    def mark(self, *args, **kwargs):
        '''
      The mark element represents a run of text in one document marked or
      highlighted for reference purposes, due to its relevance in another context.
      When used in a quotation or other block of text referred to from the prose,
      it indicates a highlight that was not originally present but which has been
      added to bring the reader's attention to a part of the text that might not
      have been considered important by the original author when the block was
      originally written, but which is now under previously unexpected scrutiny.
      When used in the main prose of a document, it indicates a part of the
      document that has been highlighted due to its likely relevance to the user's
      current activity.
      '''
        return self.stack(typ="mark", *args, **kwargs)
    
    def ruby(self, *args, **kwargs):
        '''
      The ruby element allows one or more spans of phrasing content to be marked
      with ruby annotations. Ruby annotations are short runs of text presented
      alongside base text, primarily used in East Asian typography as a guide for
      pronunciation or to include other annotations. In Japanese, this form of
      typography is also known as furigana.
      '''
        return self.stack(typ="ruby", *args, **kwargs)
    
    def rt(self, *args, **kwargs):
        '''
      The rt element marks the ruby text component of a ruby annotation.
      '''
        return self.stack(typ="rt", *args, **kwargs)
    
    def rp(self, *args, **kwargs):
        '''
      The rp element can be used to provide parentheses around a ruby text
      component of a ruby annotation, to be shown by user agents that don't support
      ruby annotations.
      '''
        return self.stack(typ="rp", *args, **kwargs)
    
    def bdi(self, *args, **kwargs):
        '''
      The bdi element represents a span of text that is to be isolated from its
      surroundings for the purposes of bidirectional text formatting.
      '''
        return self.stack(typ="bdi", *args, **kwargs)
    
    def bdo(self, *args, **kwargs):
        '''
      The bdo element represents explicit text directionality formatting control
      for its children. It allows authors to override the Unicode bidirectional
      algorithm by explicitly specifying a direction override.
      '''
        return self.stack(typ="bdo", *args, **kwargs)
    
    def span(self, *args, **kwargs):
        '''
      The span element doesn't mean anything on its own, but can be useful when
      used together with the global attributes, e.g. class, lang, or dir. It
      represents its children.
      '''
        return self.stack(typ="span", *args, **kwargs)
    
    def br(self, *args, **kwargs):
      '''
      The br element represents a line break.
      '''
      kwargs["is_single"] = True # TODO
      return self.stack(typ="br", *args, **kwargs)
    
    def wbr(self, *args, **kwargs):
      '''
      The wbr element represents a line break opportunity.
      '''
      kwargs["is_single"] = True # TODO
      return self.stack(typ="wbr", *args, **kwargs)
    
    
    
    # Edits
    
    def ins(self, *args, **kwargs):
        '''
      The ins element represents an addition to the document.
      '''
        return self.stack(typ="ins", *args, **kwargs)
    
    def del_(self, *args, **kwargs):
        '''
      The del element represents a removal from the document.
      '''
        return self.stack(typ="del_", *args, **kwargs)
    
    
    # Embedded content
    
    def img(self, *args, **kwargs):
        '''
      An img element represents an image.
      '''
        kwargs["is_single"] = True # TODO
        return self.stack(typ="img", *args, **kwargs)
    
    def iframe(self, *args, **kwargs):
        '''
      The iframe element represents a nested browsing context.
      '''
        return self.stack(typ="iframe", *args, **kwargs)
    
    def embed(self, *args, **kwargs):
        '''
      The embed element represents an integration point for an external (typically
      non-HTML) application or interactive content.
      '''
        kwargs["is_single"] = True # TODO
        return self.stack(typ="embed", *args, **kwargs)
    
    def object_(self, *args, **kwargs):
        '''
      The object element can represent an external resource, which, depending on
      the type of the resource, will either be treated as an image, as a nested
      browsing context, or as an external resource to be processed by a plugin.
      '''
        return self.stack(typ="object_", *args, **kwargs)
    _object = object_
    
    def param(self, *args, **kwargs):
        '''
      The param element defines parameters for plugins invoked by object elements.
      It does not represent anything on its own.
      '''
        kwargs["is_single"] = True # TODO
        return self.stack(typ="param", *args, **kwargs)
    
    def video(self, *args, **kwargs):
        '''
      A video element is used for playing videos or movies, and audio files with
      captions.
      '''
        return self.stack(typ="video", *args, **kwargs)
    
    def audio(self, *args, **kwargs):
        '''
      An audio element represents a sound or audio stream.
      '''
        return self.stack(typ="audio", *args, **kwargs)
    
    def source(self, *args, **kwargs):
        '''
      The source element allows authors to specify multiple alternative media
      resources for media elements. It does not represent anything on its own.
      '''
        kwargs["is_single"] = True # TODO
        return self.stack(typ="source", *args, **kwargs)
    
    def track(self, *args, **kwargs):
        '''
      The track element allows authors to specify explicit external timed text
      tracks for media elements. It does not represent anything on its own.
      '''
        kwargs["is_single"] = True # TODO
        return self.stack(typ="track", *args, **kwargs)
    
    def canvas(self, *args, **kwargs):
        '''
      The canvas element provides scripts with a resolution-dependent bitmap
      canvas, which can be used for rendering graphs, game graphics, or other
      visual images on the fly.
      '''
        return self.stack(typ="canvas", *args, **kwargs)
    
    def map_(self, *args, **kwargs):
        '''
      The map element, in conjunction with any area element descendants, defines an
      image map. The element represents its children.
      '''
        return self.stack(typ="map_", *args, **kwargs)
    
    def area(self, *args, **kwargs):
        '''
      The area element represents either a hyperlink with some text and a
      corresponding area on an image map, or a dead area on an image map.
      '''
        kwargs["is_single"] = True # TODO
        return self.stack(typ="area", *args, **kwargs)
    
    
    # Tabular data
    
    def table(self, *args, **kwargs):
        '''
      The table element represents data with more than one dimension, in the form
      of a table.
      '''
        return self.stack(typ="table", *args, **kwargs)
    
    def caption(self, *args, **kwargs):
        '''
      The caption element represents the title of the table that is its parent, if
      it has a parent and that is a table element.
      '''
        return self.stack(typ="caption", *args, **kwargs)
    
    def colgroup(self, *args, **kwargs):
        '''
      The colgroup element represents a group of one or more columns in the table
      that is its parent, if it has a parent and that is a table element.
      '''
        return self.stack(typ="colgroup", *args, **kwargs)
    
    def col(self, *args, **kwargs):
        '''
      If a col element has a parent and that is a colgroup element that itself has
      a parent that is a table element, then the col element represents one or more
      columns in the column group represented by that colgroup.
      '''
        kwargs["is_single"] = True # TODO
        return self.stack(typ="col", *args, **kwargs)
    
    def tbody(self, *args, **kwargs):
        '''
      The tbody element represents a block of rows that consist of a body of data
      for the parent table element, if the tbody element has a parent and it is a
      table.
      '''
        return self.stack(typ="tbody", *args, **kwargs)
    
    def thead(self, *args, **kwargs):
        '''
      The thead element represents the block of rows that consist of the column
      labels (headers) for the parent table element, if the thead element has a
      parent and it is a table.
      '''
        return self.stack(typ="thead", *args, **kwargs)
    
    def tfoot(self, *args, **kwargs):
        '''
      The tfoot element represents the block of rows that consist of the column
      summaries (footers) for the parent table element, if the tfoot element has a
      parent and it is a table.
      '''
        return self.stack(typ="tfoot", *args, **kwargs)
    
    def tr(self, *args, **kwargs):
        '''
      The tr element represents a row of cells in a table.
      '''
        return self.stack(typ="tr", *args, **kwargs)
    
    def td(self, *args, **kwargs):
        '''
      The td element represents a data cell in a table.
      '''
        return self.stack(typ="td", *args, **kwargs)
    
    def th(self, *args, **kwargs):
        '''
      The th element represents a header cell in a table.
      '''
        return self.stack(typ="th", *args, **kwargs)
    
    
    
    # Forms
    
    def form(self, *args, **kwargs):
        '''
      The form element represents a collection of form-associated elements, some of
      which can represent editable values that can be submitted to a server for
      processing.
      '''
        return self.stack(typ="form", *args, **kwargs)
    
    def fieldset(self, *args, **kwargs):
        '''
      The fieldset element represents a set of form controls optionally grouped
      under a common name.
      '''
        return self.stack(typ="fieldset", *args, **kwargs)
    
    def legend(self, *args, **kwargs):
        '''
      The legend element represents a caption for the rest of the contents of the
      legend element's parent fieldset element, if any.
      '''
        return self.stack(typ="legend", *args, **kwargs)
    
    def label(self, *args, **kwargs):
        '''
      The label represents a caption in a user interface. The caption can be
      associated with a specific form control, known as the label element's labeled
      control, either using for attribute, or by putting the form control inside
      the label element itself.
      '''
        return self.stack(typ="label", *args, **kwargs)
    
    def input_(self, *args, **kwargs):
        '''
      The input element represents a typed data field, usually with a form control
      to allow the user to edit the data.
      '''
        kwargs["is_single"] = True # TODO
        return self.stack(typ="input", *args, **kwargs)
    input = _input = input_
    
    def button(self, *args, **kwargs):
        '''
      The button element represents a button. If the element is not disabled, then
      the user agent should allow the user to activate the button.
      '''
        return self.stack(typ="button", *args, **kwargs)
    
    def select(self, *args, **kwargs):
        '''
      The select element represents a control for selecting amongst a set of
      options.
      '''
        return self.stack(typ="select", *args, **kwargs)
    
    def datalist(self, *args, **kwargs):
        '''
      The datalist element represents a set of option elements that represent
      predefined options for other controls. The contents of the element represents
      fallback content for legacy user agents, intermixed with option elements that
      represent the predefined options. In the rendering, the datalist element
      represents nothing and it, along with its children, should be hidden.
      '''
        return self.stack(typ="datalist", *args, **kwargs)
    
    def optgroup(self, *args, **kwargs):
        '''
      The optgroup element represents a group of option elements with a common
      label.
      '''
        return self.stack(typ="optgroup", *args, **kwargs)
    
    def option(self, *args, **kwargs):
        '''
      The option element represents an option in a select element or as part of a
      list of suggestions in a datalist element.
      '''
        return self.stack(typ="option", *args, **kwargs)
    
    def textarea(self, *args, **kwargs):
        '''
      The textarea element represents a multiline plain text edit control for the
      element's raw value. The contents of the control represent the control's
      default value.
      '''
        return self.stack(typ="textarea", *args, **kwargs)
    
    def keygen(self, *args, **kwargs):
        '''
      The keygen element represents a key pair generator control. When the
      control's form is submitted, the private key is stored in the local keystore,
      and the public key is packaged and sent to the server.
      '''
        kwargs["is_single"] = True # TODO
        return self.stack(typ="keygen", *args, **kwargs)
    
    def output(self, *args, **kwargs):
        '''
      The output element represents the result of a calculation.
      '''
        return self.stack(typ="output", *args, **kwargs)
    
    def progress(self, *args, **kwargs):
        '''
      The progress element represents the completion progress of a task. The
      progress is either indeterminate, indicating that progress is being made but
      that it is not clear how much more work remains to be done before the task is
      complete (e.g. because the task is waiting for a remote host to respond), or
      the progress is a number in the range zero to a maximum, giving the fraction
      of work that has so far been completed.
      '''
        return self.stack(typ="progress", *args, **kwargs)
    
    def meter(self, *args, **kwargs):
        '''
      The meter element represents a scalar measurement within a known range, or a
      fractional value; for example disk usage, the relevance of a query result, or
      the fraction of a voting population to have selected a particular candidate.
      '''
        return self.stack(typ="meter", *args, **kwargs)
    
    
    # Interactive elements
    
    def details(self, *args, **kwargs):
        '''
      The details element represents a disclosure widget from which the user can
      obtain additional information or controls.
      '''
        return self.stack(typ="details", *args, **kwargs)
    
    def summary(self, *args, **kwargs):
        '''
      The summary element represents a summary, caption, or legend for the rest of
      the contents of the summary element's parent details element, if any.
      '''
        return self.stack(typ="summary", *args, **kwargs)
    
    def command(self, *args, **kwargs):
        '''
      The command element represents a command that the user can invoke.
      '''
        kwargs["is_single"] = True # TODO
        return self.stack(typ="command", *args, **kwargs)
    
    def menu(self, *args, **kwargs):
        '''
      The menu element represents a list of commands.
      '''
        return self.stack(typ="menu", *args, **kwargs)
