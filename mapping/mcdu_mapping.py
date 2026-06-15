import json

class McduMapping():
    MCDU_BASE_PREFIX = "AirbusFBW/MCDU"

    def __init__(self, mcdu_type: int) -> None:    
        if mcdu_type not in (1, 2, 3):
            raise ValueError(f"Unknown MCDU type: {mcdu_type}, supported only 1, 2 and 3")

        self.mapping = self.read_mcdu_key_mapping()
        self.mapping = self.set_mcdu_type_to_mappings(mcdu_type, self.mapping)

    def get(self, command):
        if command not in self.mapping:
            return None
        return self.mapping[command]

    def read_mcdu_key_mapping(self) -> dict[str, str]:
        with open('config/key_config.json', 'r') as config_file:
            data = json.load(config_file)
            if "mcdu" not in data:
                raise ValueError("mcdu object not exists in map_config.json")
            return data["mcdu"]

    def set_mcdu_type_to_mappings(self, mcdu_type: int, map_config: dict[str, str]) -> dict[str, str]:
        target_prefix = f"{self.MCDU_BASE_PREFIX}{mcdu_type}"

        for key, value in map_config.items():
            if value.startswith(self.MCDU_BASE_PREFIX) and not value.startswith(target_prefix):
                map_config[key] = target_prefix + value[len(self.MCDU_BASE_PREFIX):]

        return map_config