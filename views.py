from django.shortcuts import render,redirect,get_object_or_404
from django.http import HttpResponseBadRequest,HttpResponse, JsonResponse
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import check_password,make_password
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import Customer,Product,Order,Cart,Category,Complaints,Reply,Ordersub


# Create your views here.

def nav(request):
    return render(request,'nav.html')

def index(request):
    max_products = 4
    latest_products = Product.objects.filter(category='Men').order_by('-created_at')[:max_products]
    women_latest=Product.objects.filter(category='Women').order_by('-created_at')[:max_products]
    kids_latest=Product.objects.filter(category='Kids').order_by('-created_at')[:max_products]
    accs_latest=Product.objects.filter(category='Accessories').order_by('-created_at')[:max_products]
    return render(request,'index.html',{'latest_product':latest_products,'women_latest':women_latest,'kids_latest':kids_latest,'accs_latest':accs_latest})


def pro(request, id):
    return redirect('single_product', id=id)



#_____paginator______________________________________________

def paginate_queryset(queryset, page_number, items_per_page=9):
    paginator = Paginator(queryset, items_per_page)
    try:
        page_obj = paginator.get_page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)
    return page_obj


#______________________registration form__________________

def customer_reg(request):
    if request.method == 'POST':
        
        # Retrieve the form data
        fname = request.POST.get('fname')
        lname = request.POST.get('lname')
        email = request.POST.get('email')
        # if Customer.objects.filter(email=email).exist():
        #     return render(request,'register.html',{'error':'email already exist'})

        password1 = request.POST.get('password')
        password=make_password(password1)

        address = request.POST.get('address')
        city = request.POST.get('city')
        state = request.POST.get('state')
        postcode = request.POST.get('zip')
        number = request.POST.get('number')  
        
        

        # Create a new customer object
        reg = Customer(firstname=fname,lastname=lname,email=email,number=number,password=password,address=address,state=state,city=city,zip=postcode)
        reg.save()
          
        return redirect('login_page')

    
    return render(request, 'register.html')



#_______________login____________
def login_page(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        user = User.objects.filter(email=email).first()
        if user and user.check_password(password):
                if user.is_superuser:  # Admin user
                    login(request, user)  # Log in the admin
                    return redirect('admin1')
        else:
            try:
                customer_instance = Customer.objects.get(email=email)
                if check_password(password, customer_instance.password):
                    # Login user and redirect to index
                    request.session['customer_id'] = customer_instance.id
                    return redirect('index')
                else:
                   return HttpResponse(
                        "<script>alert('Invalid username or password. Please try again.'); window.location.href=window.location.href;</script>"
                    )
            except Customer.DoesNotExist:
                    return HttpResponse(
                        "<script>alert('Invalid username or password. Please try again.'); window.location.href=window.location.href;</script>"
                    )

    return render(request, 'login.html')
    
 

#________________ products_men________________________

def products_men(request):
    promen=Product.objects.filter(category=Category.MEN )
    page_number = request.GET.get('page')
    page_obj = paginate_queryset(promen, page_number)
    return render(request, 'product_men.html', {'page_obj': page_obj})



#________________ products_women________________________


def products_women(request):
    prowomen=Product.objects.filter(category=Category.WOMEN)
    page_number = request.GET.get('page')
    page_obj = paginate_queryset(prowomen, page_number)
    return render(request, 'products_women.html', {'page_obj': page_obj})
#________________  products_kid________________________

    
def products_kids(request):
    kiddo=Product.objects.filter(category=Category.KIDS)
    page_number = request.GET.get('page')  
    page_obj = paginate_queryset(kiddo, page_number) 
    return render(request, 'product_kids.html', {'page_obj': page_obj})

#________________ accessories________________________
 
def products_access(request):
    access=Product.objects.filter(category=Category.ACCESSORIES)
    page_number = request.GET.get('page')  
    page_obj = paginate_queryset(access, page_number) 
    return render(request, 'product_men.html', {'page_obj': page_obj})
   



#____________________ Single product view____________________________

def single_product(request, id):
    singpro = get_object_or_404(Product, id=id)

    if request.method == 'POST':
        try:
            qty = int(request.POST.get('quantity', 1))
            if qty < 1:
                raise ValueError("Quantity must be at least 1.")

            # Add the product to the cart
            customer_id = request.session.get('customer_id')
            customer = get_object_or_404(Customer, id=customer_id)
            total_price = singpro.price * qty
            cart_item, created = Cart.objects.get_or_create(
                customer=customer,
                product=singpro,
                defaults={'quantity': qty, 'amount': total_price}
            )
            if not created:
                cart_item.quantity += qty
                cart_item.amount = cart_item.quantity * singpro.price
                cart_item.save()

            messages.success(request, f"{singpro.productname} added to cart.")
            return redirect('cart_view')
        except (ValueError, TypeError):
            messages.error(request, "Invalid quantity. Please try again.")

    return render(request, 'single-product.html', {'singpro': singpro})


# ____________Cart view___________________________________

def cart_view(request):
    customer_id = request.session.get('customer_id')
    if not customer_id:
        return redirect('login_page')

    customer = get_object_or_404(Customer, id=customer_id)
    cart_items = Cart.objects.filter(customer=customer).select_related('product')

    total_amount = sum(item.amount for item in cart_items)

    return render(request, 'cart.html', {
        'cart_items': cart_items,
        'total_amount': total_amount,
        'customer': customer,
    })

# ___________________________Cart Delete_____________
def cart_delete(request, id):
    customer_id = request.session.get('customer_id')
    if not customer_id:
        return redirect('login_page')

    customer = get_object_or_404(Customer, id=customer_id)
    cart_item = get_object_or_404(Cart, id=id, customer=customer)
    cart_item.delete()

    messages.success(request, "Item has been removed from your cart.")
    return redirect('cart_view')



# _____________Create Order from Cart_________________
def create_order_from_cart(customer, address):
    cart_items = Cart.objects.filter(customer=customer).select_related('product')

    if not cart_items.exists():
        return None, "Your cart is empty."

    # Calculate grand total
    grand_total = sum(item.amount for item in cart_items)

    # Create the Order
    order = Order.objects.create(
        customer=customer,
        address=address,
        total_products=len(cart_items),
        grand_total=grand_total,
        status='Pending',
    )

    # Create Ordersub entries
    for cart_item in cart_items:
        Ordersub.objects.create(
            order=order,
            product=cart_item.product,
            quantity=cart_item.quantity,
            price_per_unit=cart_item.product.price,
            total_price=cart_item.amount,  # Use pre-calculated amount
        )

    # Clear the cart
    cart_items.delete()

    return order, None

# ________________________Create Order for Single____________________
def create_order_for_single_item(customer, cart_item_id, address):
    cart_item = get_object_or_404(Cart, id=cart_item_id, customer=customer)

    # Create the Order
    grand_total = cart_item.amount
    order = Order.objects.create(
        customer=customer,
        address=address,
        total_products=1,
        grand_total=grand_total,
        status='Pending',
    )

    # Create Ordersub entry
    Ordersub.objects.create(
        order=order,
        product=cart_item.product,
        quantity=cart_item.quantity,
        price_per_unit=cart_item.product.price,
        total_price=cart_item.amount,
    )

    return order

# ________________Buy All View _______________________
#  Preview the invoice for all cart items
def buy_all(request):
    customer_id = request.session.get('customer_id')
    if not customer_id:
        messages.error(request, "Please log in to proceed.")
        return redirect('login_page')

    customer = get_object_or_404(Customer, id=customer_id)
    cart_items = Cart.objects.filter(customer=customer).select_related('product')

    if not cart_items.exists():
        messages.error(request, "Your cart is empty.")
        return redirect('cart_view')

    if not customer.address:
        messages.error(request, "Please provide an address before proceeding.")
        return redirect('cart_view')

    total_amount = sum(item.amount for item in cart_items)
    return render(request, 'invoice.html', {
        'cart_items': cart_items,
        'total_amount': total_amount,
        'address': customer.address
    })


#____________________________ Buy Single View_____________________  
# Redirect to invoice preview for a single cart item
def buy_single(request, cart_item_id):
    customer_id = request.session.get('customer_id')
    if not customer_id:
        messages.error(request, "Please log in to proceed.")
        return redirect('login_page')

    customer = get_object_or_404(Customer, id=customer_id)
    cart_item = get_object_or_404(Cart, id=cart_item_id, customer=customer)
    default_address = customer.address  
    # Redirect to the invoice preview for this single item
    return render(request, 'invoice.html', {
        'cart_items': [cart_item],
        'total_amount': cart_item.amount,
        'address':customer.address
    })

#________________________________________ Confirm Order View______________________________
def confirm_order(request):
    if request.method == 'POST':
        customer_id = request.session.get('customer_id')
        if not customer_id:
            messages.error(request, "Please log in to proceed.")
            return redirect('login_page')

        customer = get_object_or_404(Customer, id=customer_id)
        address = request.POST.get('address')
        if not address:
            messages.error(request, "Please provide a delivery address.")
            return redirect('cart_view')

        cart_items = Cart.objects.filter(customer=customer).select_related('product')

        if not cart_items.exists():
            messages.error(request, "Your cart is empty.")
            return redirect('cart_view')

        grand_total = sum(item.amount for item in cart_items)

        # Create the Order
        order = Order.objects.create(
            customer=customer,
            address=address,
            total_products=len(cart_items),
            grand_total=grand_total,
            status='Pending',
        )

        # Create Ordersub entries
        for cart_item in cart_items:
            Ordersub.objects.create(
                order=order,
                product=cart_item.product,
                quantity=cart_item.quantity,
                price_per_unit=cart_item.product.price,
                total_price=cart_item.amount,
            )

        
        cart_items.delete()

        messages.success(request, f"Order placed successfully! Grand Total: ${order.grand_total:.2f}")
        return redirect('cart_view') 

    return redirect('cart_view')

# ___________________________ Invoice View_______________________________________
def invoice_view(request, order_id):
    customer_id = request.session.get('customer_id')
    if not customer_id:
        messages.error(request, "Please log in to view the invoice.")
        return redirect('login_page')

    customer = get_object_or_404(Customer, id=customer_id)

    order = get_object_or_404(Order, id=order_id, customer=customer)
    order_subs = Ordersub.objects.filter(order=order).select_related('product')

    return render(request, 'invoice.html', {'customer': customer,'order': order,'order_subs': order_subs})

#__________________________________order_history__________________________________
def order_history(request):
    customer_id = request.session.get('customer_id')
    if not customer_id:
        messages.error(request, "Please log in to view your order history.")
        return redirect('login_page')

    customer = get_object_or_404(Customer, id=customer_id)

    orders = Order.objects.filter(customer=customer).order_by('-date_placed')

    if request.method == 'POST':
        order_id = request.POST.get('order_id')
        try:
            order = Order.objects.get(id=order_id, customer=customer)
            if order.status == 'Pending':
                order.status = 'Cancelled'
                order.save()
                messages.success(request, f"Order #{order_id} has been canceled successfully.")
                if order.status == 'Cancelled':
                    order.delete()
            else:
                messages.error(request, "Only orders with 'Pending' status can be canceled.")
        except Order.DoesNotExist:
            messages.error(request, "Order not found or you don't have permission to cancel this order.")

    return render(request, 'order_history.html', { 'customer': customer, 'orders': orders })


#______________payment_page______________________________
def payment_page(request, order_id):
    customer_id = request.session.get('customer_id')
    if not customer_id:
        messages.error(request, "Please log in to proceed with the payment.")
        return redirect('login_page')

    customer = get_object_or_404(Customer, id=customer_id)
    order = get_object_or_404(Order, id=order_id, customer=customer)

    if order.status != 'Confirmed':
        messages.error(request, "Payment can only be made for orders with 'Confirmed' status.")
        return redirect('order_history')

    # Render payment gateway or instructions
    return render(request, 'payment.html', {'order': order})


#_________________About__________________________

def about(request):
    return render(request,'about.html')

#________________Contact________________________________

def contact(request):
    customer_id = request.session.get('customer_id')
    if not customer_id:
        return redirect('login_page')

    customer = get_object_or_404(Customer, id=customer_id)
    complaints = Complaints.objects.filter(customer=customer)  # Get only the logged-in customer's complaints

    if request.method == 'POST':
        subject = request.POST.get('subject')
        if subject and len(subject.strip()) > 0:
            complaint = Complaints(complaint=subject.strip(), customer=customer)
            complaint.save()
            messages.success(request, "Your complaint has been submitted successfully!")
            return redirect('contact')
        else:
            messages.error(request, "Please provide a valid complaint.")
    
    return render(request, 'contact.html', {'customer': customer, 'complaints': complaints})
#_____________________Reply_id________________________

def reply_id(request, id):
    complaint = get_object_or_404(Complaints, id=id)
    return redirect('view_reply', id=complaint.id)

#______________________logout________________________

def logout(request):
    if 'customer_id' in request.session:
        del request.session['customer_id']
    messages.success(request, "You have been logged out successfully.")#add url
    return redirect('login_page')

#___________________order_status_______________________

def order_status(request, id):
    order = get_object_or_404(Order, id=id) 

    if request.method == 'POST':
        status = request.POST.get('status')

        
        if status in dict(Order.STATUS_CHOICES).keys():
            order.status = status  
            order.save()  # Saves the updated order

        else:
            return HttpResponseBadRequest("Invalid status value")  
        if status == 'cancelled':
            order.delete() 

    return redirect('admin1')

#____________________view_order_details_________________

def order_details(request,id):
    order=Order.objects.get(id=id)
    order_items=Ordersub.objects.filter(order=order)
    total_amount = sum(item.total_price for item in order_items)
    context={
        'order':order,
        'order_items':order_items,
        'total_amount':total_amount
    }
    return render(request,'viewproductdetails.html',context)


#_____________________admin______________________________

def admin1(request):
    ordr=Order.objects.all().order_by('-id')
    procount= Product.objects.all().count()
    odrcount=ordr.count()
    c=Customer.objects.all().count
    co=Complaints.objects.all().count()
    
    categories = Category.choices 
    uploaded_image_url = None 

    if request.method == 'POST':
        productname = request.POST.get('productname')
        image = request.FILES.get('image')
        price = request.POST.get('price')
        description = request.POST.get('description')
        category = request.POST.get('category')

        # Make sure all required fields are present
        if not category:
            return redirect('admin1')

        # Create the product object
        pro = Product(
            productname=productname,
            image=image,
            price=price,
            description=description,
            category=category
        )
        pro.save()

       
        return redirect('admin1')

    return render(request, 'admin123.html', {'cate': categories,'ordr':ordr,'procount':procount,'odrcount':odrcount,'c':c,'co':co})#add order to admin page 



#_________________view_products____________________________________

def view_products(request):
    products = Product.objects.all()
    
    return render(request, 'productlist.html', {'products': products})


#__________________view_customers___________________________

def view_customers(request):
    customer_details= Customer.objects.all()
    return render(request,'viewcustomers.html',{'customer_details':customer_details})

#____________________View_Customer______________________________

def view_customer(request, id):
    customer = get_object_or_404(Customer, id=id)
    return render(request, 'singlecustomer.html', {'customer': customer})


#_____________________Update_Product______________________________

def update_product(request, id):
  
    product = get_object_or_404(Product, id=id)
    categories = Category.choices  # Use choices directly from Category

    if request.method == 'POST':
        product.productname = request.POST.get('productname', product.productname)

        if 'image' in request.FILES:
            product.image = request.FILES['image']
        product.price = request.POST.get('price', product.price)
        product.description = request.POST.get('description', product.description)

        # Validate and update category
        category_value = request.POST.get('category')
        if category_value in dict(categories).keys():  # Check if category_value is valid
            product.category = category_value
        else:
            messages.error(request, "Invalid category selected.")
            return render(request, 'updateproduct.html', {'product': product, 'categories': categories})

        product.save()
        messages.success(request, "Product updated successfully!")
        return redirect('view_products')
    return render(request,'updateproduct.html',{'product': product,'categories': categories})


#_____________________delete_product_____________________

def delete_product(request,id):
     prodelete = get_object_or_404(Product, id=id)
     prodelete.delete()
     messages.success(request, "Item has been removed from the products.")
     return redirect('view_products')

#______________________view_complaints________________________

def view_complaints(request):
    if request.session.get('is_admin', True):  
        viewcomplaints = Complaints.objects.all()  
    else:
        customer_id = request.session.get('customer_id')  
        if not customer_id:
            return redirect('login_page') 
        customer = get_object_or_404(Customer, id=customer_id)
        viewcomplaints = Complaints.objects.filter(customer=customer)  
    return render(request, 'complaints.html', {'viewcomplaints': viewcomplaints})

#________________________Reply________________________

def reply(request, id):
    complaint = get_object_or_404(Complaints, id=id)

    customer_id = request.session.get('customer_id')
    if not customer_id:
        return redirect('login_page')

    if request.session.get('is_admin', False) or complaint.customer.id == customer_id:
        if request.method == "POST":
            reply_text = request.POST.get('reply')
            if reply_text:
                # Create a reply
                Reply.objects.create(complaint=complaint, reply=reply_text)
                complaint.replied = True
                complaint.save()
                messages.success(request, "Your reply has been sent successfully!")
                return redirect('view_complaints')
        else:
            messages.error(request, "Please write a reply.")
    else:
        messages.error(request, "You are not authorized to reply to this complaint.")

    return redirect('view_complaints')

#__________________________View_reply______________________________

def view_reply(request):
    
    customer_id = request.session.get('customer_id')
    if not customer_id:
        return redirect('login_page')  

    
    complaints = Complaints.objects.filter(customer_id=customer_id).order_by('-id')

    # Fetch replies for each complaint
    complaints_with_replies = []
    for complaint in complaints:
        replies = complaint.replies.all()  
        complaints_with_replies.append({
            'complaint': complaint,
            'replies': replies
        })

    
    return render(request, 'viewreplies.html', {'complaints_with_replies': complaints_with_replies})


#_______________________Update_user___profile_______________________

def update_profile(request):
   
    customer_id = request.session.get('customer_id')
    if not customer_id:
        return redirect('login_page')  
    customer = get_object_or_404(Customer, id=customer_id)

    if request.method == 'POST':
        # Update customer details with form data
        customer.firstname = request.POST.get('firstname')
        customer.lastname = request.POST.get('lastname')
        customer.email = request.POST.get('email')
        customer.number = request.POST.get('number')
        customer.address = request.POST.get('address')
        customer.state = request.POST.get('state')
        customer.city = request.POST.get('city')
        customer.zip = request.POST.get('zip')

        try:
            customer.save()
            messages.success(request, 'Profile updated successfully!')
        except Exception as e:
            messages.error(request, 'An error occurred while updating your profile. Please try again.')

        return redirect('index')

    return render(request, 'updateuser.html', {'customer': customer})



#payment method not added so check it

# views.py
from django.http import JsonResponse
from .models import Product

def get_product_details(request):
    product_name = request.GET.get('productname')
    if not product_name:
        return JsonResponse({'error': 'Product name is required'}, status=400)

    products = Product.objects.filter(productname__icontains=product_name)

    if not products.exists():
        return JsonResponse({'error': 'Product not found'}, status=404)

    # If multiple products are found, return details of the first match
    product = products.first()
    data = {
        'productname': product.productname,
        'price': product.price,
        'description': product.description,
        'category': product.category,
        'image_url': product.image.url,
    }
    return JsonResponse(data)

