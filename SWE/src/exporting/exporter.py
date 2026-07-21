import json
import os
from typing import List
from collections import Counter
from analysis.models import DetectionResult


class JSONExporter:
    def __init__(self, output_path: str):
        self.output_path = output_path
        self.temp_path = f"{output_path}.tmp"
        # Use a Counter to track the frequency of each unique technology
        self.technology_frequencies = Counter()

        # Initialize a clean temp file
        open(self.temp_path, 'w').close()

    def append_result(self, domain_url: str, findings: List[DetectionResult]):
        """Streams a single domain's results into a temporary JSONL file."""
        tech_count = len(findings)

        # Increment the frequency counter for each technology found on this domain
        for f in findings:
            self.technology_frequencies[f.technology_name] += 1

        record = {
            "domain": domain_url,
            "technologies_count": tech_count,
            "technologies": [
                {
                    "name": f.technology_name,
                    "confidence": f.confidence,
                    "proofs": f.proofs
                } for f in findings
            ]
        }

        # Append to temp file instantly (no memory buildup for domain records)
        with open(self.temp_path, 'a', encoding='utf-8') as f:
            f.write(json.dumps(record) + '\n')

    def finalize(self):
        """Stitches the unique counts, frequencies, and the temporary records into valid JSON."""
        print(f"Finalizing export to {self.output_path}...")

        # The number of unique technologies is simply the number of keys in our Counter
        unique_tech_count = len(self.technology_frequencies)

        with open(self.output_path, 'w', encoding='utf-8') as final_out, \
                open(self.temp_path, 'r', encoding='utf-8') as temp_in:

            # Write the required headers with the total unique count and frequency map
            final_out.write('{\n')
            final_out.write(f'  "total_unique_technologies_found": {unique_tech_count},\n')

            # Format the frequency dictionary nicely into the JSON
            freq_json = json.dumps(dict(self.technology_frequencies), indent=2).replace('\n', '\n  ')
            final_out.write(f'  "technology_frequencies": {freq_json},\n')

            final_out.write('  "results": [\n')

            # Stream the temporary records into the final array
            first_record = True
            for line in temp_in:
                if not first_record:
                    final_out.write(',\n')

                # Indent the line for pretty formatting
                final_out.write('    ' + line.strip())
                first_record = False

            # Close the JSON structure
            final_out.write('\n  ]\n')
            final_out.write('}\n')

        # Clean up the temporary file
        os.remove(self.temp_path)

        print(f"Export complete. Unique technologies identified: {unique_tech_count}")
        print(f"Distribution: {dict(self.technology_frequencies)}")