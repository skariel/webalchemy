
class table:
    def __init__(self,rdoc,rows,cols,has_header=True,has_index=True,on_add_row=None,on_add_data_cell=None,on_add_header_cell=None):
        self.rdoc= rdoc
        self.element= rdoc.element('table')
        vn= '#'+self.element.varname
        self.rule_table= rdoc.stylesheet.rule(vn)
        self.rule_row= rdoc.stylesheet.rule(vn+' > tr')
        self.rule_row_hover= rdoc.stylesheet.rule(vn+' > tr:hover')
        self.rule_datacell= rdoc.stylesheet.rule(vn+' > tr > td')
        self.rule_datacell_hover= rdoc.stylesheet.rule(vn+' > tr > td:hover')
        self.rule_headercell= rdoc.stylesheet.rule(vn+' > tr > th')
        self.rule_headercell_hover= rdoc.stylesheet.rule(vn+' > tr > th:hover')
        self.rule_row_selected= rdoc.stylesheet.rule(vn+' > tr.selected')
        self.rule_row_selected_hover= rdoc.stylesheet.rule(vn+' > tr.selected:hover')
        self.rule_datacell_selected= rdoc.stylesheet.rule(vn+' > tr > td.selected')
        self.rule_datacell_selected_hover= rdoc.stylesheet.rule(vn+' > tr > td.selected:hover')
        self.rule_headercell_selected= rdoc.stylesheet.rule(vn+' > tr > th.selected')
        self.rule_headercell_selected_hover= rdoc.stylesheet.rule(vn+' > tr > th.selected:hover')
        self.rule_row_header= rdoc.stylesheet.rule(vn+' > tr.header')
        self.rule_row_header_hover= rdoc.stylesheet.rule(vn+' > tr.header:hover')
        self.rule_datacell_index= rdoc.stylesheet.rule(vn+' > tr > td.index')
        self.rule_datacell_index_hover= rdoc.stylesheet.rule(vn+' > tr > td.index:hover')

        # build an empty table...
        self.row_col_items={}
        self.rows=[]
        for row_ix in range(rows):
            row= self.rdoc.element('tr')
            self.rows.append(row)
            if row_ix==0 and has_header:
                row.cls.append('header')
            if on_add_row:
                on_add_row(row,row_ix)
            self.element.append(row)
            for col_ix in range(cols):
                if has_header and row_ix==0:
                    cell= self.rdoc.element('th','empty!!')
                    if on_add_header_cell:
                        on_add_header_cell(cell,row_ix,cell_ix)
                else:
                    cell= self.rdoc.element('td','empty!')
                    if on_add_data_cell:
                        on_add_data_cell(cell,row_ix,col_ix)
                if col_ix==0 and has_index:
                    cell.cls.append('index')
                row.append(cell)
                self.row_col_items[(row_ix,col_ix)]= cell

