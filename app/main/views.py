from . import main
from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.models import User, Inventory, Item, Order, Payment
from app import db
from app.email import send_email
from datetime import datetime


@main.route('/', methods=['GET'])
@login_required
def index():
    return render_template('index.html')


@main.route('/orders', methods=['GET', 'POST'])
@login_required
def orders():
    if request.method == "POST":
        item_id = request.form.get('item_type')
        quantity = request.form.get('quantity')
        owner_id = current_user.id
        supplier_id = request.form.get('supplier_id')
        unit_price = request.form.get('unit_price')
        total_price = int(quantity) * int(unit_price)

        order = Order(item_id=item_id, quantity=quantity, unit_price=unit_price,
                      total_price=total_price, supplier_id=supplier_id, owner_id=owner_id)
        db.session.add(order)
        db.session.commit()
        flash('Order has been placed successfully')

        return redirect(url_for('main.orders'))

    orders = []
    if current_user.is_supplier:
        orders = Order.query.filter_by(supplier_id=current_user.id).all()
    elif current_user.is_manager or current_user.is_admin:
        orders = Order.query.filter_by(owner_id=current_user.id).all()
    items = Item.query.all()
    suppliers = User.query.filter_by(is_supplier=True).all()
    return render_template('orders.html', orders=orders, items=items, suppliers=suppliers)


@main.route('/order/<int:id>/pay', methods=["GET"])
@login_required
def pay_order(id):
    order = Order.query.get(id)
    order.paid = True
    db.session.add(order)

    method = "Bank Transfer"

    payment = Payment(order_id=order.id, amount=order.total_price,
                      debitor_id=order.owner_id, receiver_id=order.supplier_id, method=method, payment_date=datetime.now())
    db.session.add(payment)

    db.session.commit()

    send_email(order.supplier.email, 'Payment received',
               'order/payment_received', order=order, payment_date=payment.payment_date)

    flash("Order has been paid")
    return redirect(url_for('main.orders'))


@main.route('/order/<int:id>/supply', methods=["GET"])
@login_required
def supply_order(id):
    order = Order.query.get(id)
    owner_id = order.owner_id
    supplier_id = order.supplier_id

    # Fetch the supplier's inventory and check if they have enough quantity
    supplier_inventory = Inventory.query.filter_by(
        owner_id=supplier_id, item_id=order.item_id).first()
    if supplier_inventory is None or supplier_inventory.quantity < order.quantity:
        flash("Supplier does not have enough items to supply this order")
        return redirect(url_for('main.orders'))

    # Fetch the owner's inventory or create one if it doesn't exist
    owner_inventory = Inventory.query.filter_by(
        owner_id=owner_id, item_id=order.item_id).first()
    if owner_inventory is None:
        owner_inventory = Inventory(
            item_id=order.item_id, quantity=0, unit_price=order.unit_price, owner_id=owner_id)
        db.session.add(owner_inventory)

    # Update the inventories
    owner_inventory.quantity += order.quantity
    supplier_inventory.quantity -= order.quantity

    # Mark the order as delivered
    order.delivered = True
    order.delivery_date = datetime.now()

    # Save changes within a single transaction
    try:
        db.session.commit()
        send_email(order.owner.email, 'Your order has been supplied',
                   'order/order_supplied', order=order)
        flash("Order has been successfully supplied")
    except Exception as e:
        db.session.rollback()
        flash(f"An error occurred while supplying the order: {str(e)}")

    return redirect(url_for('main.orders'))


@main.route('/payments', methods=['GET'])
@login_required
def payments():
    payments = Payment.query.filter_by(receiver_id=current_user.id).all()
    return render_template('payments.html', payments=payments)


@main.route('/inventory', methods=['GET', 'POST'])
@login_required
def inventory():
    if request.method == "POST":
        item_id = request.form.get('item_type')
        quantity = request.form.get('quantity')
        unit_price = request.form.get('unit_price')
        owner_id = current_user.id

        item = Inventory.query.filter_by(
            item_id=item_id, owner_id=owner_id).first()
        if item:
            item.quantity += int(quantity)
            db.session.add(item)
            db.session.commit()
            flash('Item has been updated')

            return redirect(url_for('main.inventory'))

        inventory = Inventory(item_id=item_id, quantity=quantity,
                              unit_price=unit_price, owner_id=owner_id)
        db.session.add(inventory)
        db.session.commit()
        flash('Inventory added successfully')

        return redirect(url_for('main.inventory'))

    inventories = Inventory.query.filter_by(owner_id=current_user.id).all()
    items = Item.query.all()
    return render_template('inventory.html', inventories=inventories, items=items)


@main.route('/order/<int:id>/delete', methods=['GET'])
@login_required
def delete_order(id):
    order = Order.query.get(id)
    db.session.delete(order)
    db.session.commit()
    flash('Order has been deleted successfully')

    return redirect(url_for('main.orders'))
