





#This method finds the kth smallest in an array by breaking problem into smaller pieces
#until we get the kth smallest element

#input: this method requires the array be unordered
#output: this method returns the kth smallest element if 

#arr = unordered array being looked through
#i = index of partition pivot
#left = start of array, left portion
#right = end of array, right portion
#kth = the number element we are looking up to when looking for smallest

def kthSmallestElement(arr, left,right,kth):
  if(kth<= right-left +1 and kth>0):
      
      i = partition(arr,left,right)
      

      if(i - left == kth-1):
        return arr[i]
      
      if(i-left > k-1):
         return kthSmallestElement(arr, left, i-1, kth)
      
      return kthSmallestElement(arr, i+1, right, kth - i + left - 1)
  

  print("Error: Invalid Index")

#This method essentially sorts a list by shifting everything around the pivot

#input: the method requires an array along with its starting and ending indexes
#output: ends up returning the position of the pivot in relation to how the list is ordered

def partition(arr,left,right):
  pivot = arr[right]
  i = left

  for x in range(left,right):
    if(arr[j]<=pivot):
        arr[i], arr[j] = arr[j], arr[i]
        i+=1

  arr[i], arr[r] = arr[r], arr[i]
   
  return i