import re

import pandas as pd
import tabula


class DamReader:
    def __init__(self, endpoint: str):
        self.endpoint = endpoint

    def read(self, date: str) -> pd.DataFrame:
        date_day, date_month, date_year = date.split('.')

        request = self.endpoint.format(date_day, date_month, date_year)

        tables = tabula.read_pdf(request, pages='all')
        return self.preprocess(tables)

    def preprocess(self, tables):
        def convert_to_float(value: str) -> list[float]:
            # Extract all numeric parts from the string
            matches = re.findall(r'(\d{1,3}(?:,\d{3})*(?:,\d+)?)(%?)', value)
            if not matches:
                raise ValueError(f"Cannot convert {value} to float")

            # Convert the extracted numeric parts to floats
            numbers = [float(match[0].replace(',', '.')) for match in matches]

            return numbers

        def index_rule(index):
            try:
                return int(index)
            except:
                return pd.NA

        def name_rule(name):
            try:
                return ('БД' + name.split('БД', maxsplit=1)[1]).split(maxsplit=1)
            except:
                return ['ERROR', 'ERROR']

        def intake_drain_rule(intake):
            try:
                return convert_to_float(intake)
            except:
                return [pd.NA, pd.NA]

        def process_first_table(df):
            processed_df = pd.DataFrame(columns=columns)

            rows = []
            # Iterate over the rows of the dataframe
            for i, row in df.iterrows():
                # Split the first column into three parts
                parts = row[0].split(maxsplit=2)

                parts.extend(convert_to_float(row[1]))

                parts.extend(convert_to_float(row[2]))

                rows.append(parts)

            return pd.DataFrame(rows, columns=columns)

        def process_later_tables(df):
            def process_row(row):
                out_row = [index_rule(row[0])]
                magic_number = 0  # FUCK ME I DONT EVEN HAVE A BASIC GIST OF WHAT THE MOTHERFUCKING FORMAT OF THIS GOD FORSAKEN TABLE SHOULD HAVE BEEN
                name_value = row[1]

                if type(row[1]) == str and row[1].split(maxsplit=1)[0] == row[1]:
                    magic_number = 1
                    name_value += ' ' + row[2]

                out_row.extend(name_rule(name_value))

                for i in range(2 + magic_number, 8 + magic_number):
                    try:
                        value = convert_to_float(row[i])
                        out_row.extend(value)
                    except:
                        out_row.append(pd.NA)

                out_row.extend(intake_drain_rule(row[8 + magic_number]))

                return out_row

            rows = [process_row(df.columns.tolist())]

            for i, row in df.iterrows():
                rows.append(process_row(row.tolist()))

            return pd.DataFrame(rows, columns=columns)

        def remove_error_rows(df: pd.DataFrame) -> pd.DataFrame:
            return df[~df.apply(lambda row: row.astype(str).str.contains('ERROR').any(), axis=1)]

        columns = ['number', 'water_body_directorate', 'dam_name', 'total_volume', 'dead_volume', 'available_volume',
                   'available_volume_percent', 'available_useful_volume', 'available_useful_volume_percent', 'water_intake',
                   'water_drain']

        df = tables[0]
        start_index = None

        # Find the start index
        for i, row in df.iterrows():
            if row[0] == 'No БД Язовир':
                start_index = i + 4
                break

        if start_index is None:
            return pd.DataFrame()  # Return an empty DataFrame if the start index is not found

        # Extract rows starting from start_index
        useful_data = df.iloc[start_index:]

        useful_data = process_first_table(useful_data)

        data_cont = []

        for table in tables[1:]:
            df = table
            useful_df_data = pd.DataFrame()

            nan_count = 0
            for row in df.iterrows():
                row = row[1]
                if row.isna().all():
                    nan_count += 1
                    if nan_count == 4:
                        break
                else:
                    nan_count = 0
                    useful_df_data = pd.concat([useful_df_data, pd.DataFrame([row])])

            data_cont.append(useful_df_data)

            if nan_count == 4:
                break

        for df in data_cont:
            if df.empty:
                continue

            useful_data = pd.concat([useful_data, process_later_tables(df)], ignore_index=True)

        useful_data = remove_error_rows(useful_data)
        return useful_data


if __name__ == '__main__':
    DAMS_ENDPOINT = 'https://www.moew.government.bg/static/media/ups/tiny/Daily%20Bulletin/{}{}{}_Bulletin_Daily.pdf'

    dam_reader = DamReader(DAMS_ENDPOINT)

    date = '01.01.2021'

    data = dam_reader.read(date)
