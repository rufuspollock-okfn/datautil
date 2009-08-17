import swiss.tabular

class TestTranspose:

    def test_1(self):
        inlist = [
                [ 0, 1 ],
                [ 1, 0 ],
                ]
        exp = [
                ( 0, 1 ),
                ( 1, 0 ),
                ]
        out = swiss.tabular.transpose(inlist)
        assert out == exp, out

class TestPivot:
    td = swiss.tabular.TabularData(
            header=['Name','Year','Value'],
            data=[
                ['x',2004,1],
                ['y',2004,2],
                ['y',2005,4],
                ['x',2005,3],
            ],
        )

    def test_pivot_with_tabular(self):
        out = swiss.tabular.pivot(self.td, 1, 0, 2)
        assert out.data[0] == [2004, 1, 2]
        assert out.data[-1] == [2005, 3, 4]

    def test_pivot_with_tabular_2(self):
        out = swiss.tabular.pivot(self.td, 'Year', 'Name', 'Value')
        assert out.data[0] == [2004, 1, 2]

    def test_pivot_simple_list(self):
        out = swiss.tabular.pivot(self.td.data, 1, 0, 2)
        assert out.data[0] == [2004, 1, 2]

