class MaxHeap:
    def __init__(self):
        self.heap = []

    def parent(self, i):
        return (i - 1) // 2

    def left_child(self, i):
        return 2 * i + 1

    def right_child(self, i):
        return 2 * i + 2

    def insert(self, key):
        self.heap.append(key)
        i = len(self.heap) - 1
        while i > 0 and self.heap[self.parent(i)][0] <= self.heap[i][0]:
            self.heap[self.parent(i)], self.heap[i] = self.heap[i], self.heap[self.parent(i)]
            i = self.parent(i)

    def heapify(self, i):
        largest = i
        left = self.left_child(i)
        right = self.right_child(i)
        if left < len(self.heap) and self.heap[left][0] >= self.heap[largest][0]:
            largest = left
        if right < len(self.heap) and self.heap[right][0] >= self.heap[largest][0]:
            largest = right
        if largest != i:
            self.heap[i], self.heap[largest] = self.heap[largest], self.heap[i]
            self.heapify(largest)

    def extract_max(self):
        if len(self.heap) == 0:
            return None
        max_element = self.heap[0]
        self.heap[0] = self.heap[-1]
        del self.heap[-1]
        self.heapify(0)
        return max_element

    def print_heap(self):
        print("Heap in order:")
        for item in self.heap:
            print(item, end=" ")
        print()

    def print_sorted_heap(self):
        print("Sorted Heap:")
        heap_copy = self.heap.copy()
        while heap_copy:
            max_element = self.extract_max()
            print(max_element, end=" ")
        print()


if __name__ == "__main__":
    heap = MaxHeap()
    heap.insert((5.0, "apple"))
    heap.insert((3.5, "banana"))
    heap.insert((-7.2, "orange"))
    heap.insert((4.1, "grape"))
    heap.insert((6.8, "melon"))

    heap.print_heap()
    heap.print_sorted_heap()
