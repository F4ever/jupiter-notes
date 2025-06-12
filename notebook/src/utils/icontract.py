from IPython.core.display import display_markdown
from web3.contract import Contract

from utils.table import format_abi, format_table


class IContract(Contract):
    def generate_functions_spec(self, search: str):
        mark = ''

        # Constants
        views = sorted([func for func in self.all_functions() if func.abi['stateMutability'] in ['constant', 'view', 'pure']], key=lambda f: f.abi['name'])
        if views:
            mark += self._generate_functions_spec(views, search)

        mark += '-' * 20

        methods = sorted([func for func in self.all_functions() if func.abi['stateMutability'] not in ['constant', 'view', 'pure']], key=lambda f: f.abi['name'])
        if methods:
            # mark += 'Methods list:'
            mark += self._generate_functions_spec(methods, search)

        if not views and not methods:
            mark += 'No views or methods found.'

        return mark

    def _generate_functions_spec(self, functions: list, search: str) -> str:
        res = ''
        for func in functions:
            input_text = format_abi(func.abi['inputs'], 'input')
            output_text = format_abi(func.abi['outputs'], 'output')

            if search.lower() in func.abi['name'].lower():
                # Markdown is important
                res += f'''<details><summary><b>{func.abi['name']}</b></summary>

{input_text}

{output_text}
</details>'''
        return res

    def spoiler(self):
        spec = self.generate_functions_spec('')
        display_markdown(f"""
<details><summary>ABI</summary>

{spec}

</details>
        """, raw=True)

    def print_functions(self, search=''):
        mark = self.generate_functions_spec(search)
        display_markdown(mark, raw=True)

    def load_contract(self, func_name: str):
        result = self.functions[func_name]().call()
        return self.w3.contract.load(result)

    def pprint(self, data):
        if isinstance(data[0], tuple):
            data = [d._asdict() for d in data]

        display_markdown(
            format_table(
                data[0].keys(),
                data,
                '',
            ),
            raw=True,
        )
