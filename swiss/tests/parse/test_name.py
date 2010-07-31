import swiss.parse.name


class TestName:
    def test_parse_name_FL(self):
        name = u'Ludwig Van Beethoven'
        out = swiss.parse.name.parse_name(name)
        assert out.ln == u'Beethoven'
        assert out.fns == ['Ludwig', 'Van']

    def test_parse_name_LF_with_extra_comma(self):
        out = swiss.parse.name.parse_name('More, Sir Thomas,Saint')
        assert out.ln == 'More', out
        assert out.fns == ['Sir', 'Thomas']

    def test_parse_name_FL_normcase(self):
        name = u'Ludwig van BEETHOVEN'
        out = swiss.parse.name.parse_name(name)
        assert out.ln == 'Beethoven', out

    def test_parse_name_LF_with_title(self):
        name = u'Chandos, John [Sir]'
        out = swiss.parse.name.parse_name(name)
        assert out.ln == 'Chandos', out
        assert out.title == 'Sir', out

    def test_parse_name_FL_with_title(self):
        name = u'Sir John CHANDOS'
        out = swiss.parse.name.parse_name(name)
        assert out.ln == 'Chandos', out
        assert out.title == 'Sir', out

    def test_parse_name_FL_with_title_2(self):
        name = u'Prof Benjamin AARON'
        out = swiss.parse.name.parse_name(name)
        assert out.ln == 'Aaron', out
        assert out.title == 'Prof', out
        assert out.fns == ['Benjamin'], out
        assert str(out) == 'Aaron, Benjamin [Prof]'

    def test_parse_title_with_fullstop(self):
        name = 'Major. abc xyz'
        out = swiss.parse.name.parse_name(name)
        assert out.title == 'Major', out.title

    def test_parse_title_with_fullstop_2(self):
        name = 'Xyz, Abc [Major.]'
        out = swiss.parse.name.parse_name(name)
        print out
        assert out.title == 'Major', out.title

    def test_parse_title_with_brackets(self):
        name = 'Dickens, Gerald (Sir)'
        out = swiss.parse.name.parse_name(name)
        assert out.title == 'Sir', out.title

        name = '(Sir) Gerald Dickens'
        out = swiss.parse.name.parse_name(name)
        assert out.title == 'Sir', out.title

    def test_parse_name_FL_initials(self):
        name = 'Chekhov, A.P.'
        out = swiss.parse.name.parse_name(name)
        assert out.ln == 'Chekhov'
        assert out.fns == ['A.', 'P.'], out

    def test_strip_fullstops(self):
        name = 'George. Bosch'
        out = swiss.parse.name.normalize(name)
        assert out == 'Bosch, George'        

        name = 'George. a.p. Bosch.'
        out = swiss.parse.name.normalize(name)
        assert out == 'Bosch, George A. P.', out

        name = 'Geo.rge. Bosch'
        out = swiss.parse.name.normalize(name)
        assert out == 'Bosch, Geo. Rge', out

        name = 'Geo.Smith. Bosch'
        out = swiss.parse.name.normalize(name)
        assert out == 'Bosch, Geo. Smith', out

    def test_tostr(self):
        name = swiss.parse.name.Name(ln='Beethoven', fns=['Ludwig', 'van'])
        exp = u'Beethoven, Ludwig van'
        out = swiss.parse.name.name_tostr(name)
        assert out == exp, out

    def test_with_no_name(self):
        name = swiss.parse.name.parse_name(' ')
        assert name.ln is '', name
        out = swiss.parse.name.normalize(' ')
        assert out == '', out

    def test_surname(self):
        name = u'SCHUBERT'
        out = str(swiss.parse.name.parse_name(name))
        assert out == 'Schubert'

