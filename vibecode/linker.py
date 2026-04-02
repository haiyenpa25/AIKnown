class GraphLinker:
    def __init__(self, store):
        self.store = store

    def link_calls(self, temp_dependencies):
        """
        Thực hiện Pass 2: Khớp tên hàm (target_name) với Node ID thực tế trong CSDL.
        temp_dependencies format: [(source_node_id, target_symbol_name), ...]
        """
        for src_id, target_name in temp_dependencies:
            # Tìm Node đích dựa trên tên hàm
            target_id = self.store.find_node_by_name(target_name)
            if target_id:
                self.store.add_edge(src_id, target_id, 'CALLS')
