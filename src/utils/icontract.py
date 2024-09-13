from IPython.core.display import display_markdown
from web3.contract import Contract

from utils.table import format_abi, format_table


class IContract(Contract):
    def generate_functions_spec(self, search: str):
        mark = ''

        for func in self.all_functions():
            input_text = format_abi(func.abi['inputs'], 'input')
            output_text = format_abi(func.abi['outputs'], 'output')

            if search.lower() in func.abi['name'].lower():
                # Markdown is important
                mark += f'''<details><summary><b>{func.abi['name']}</b></summary>

{input_text}

{output_text}
</details>'''

        return mark

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
