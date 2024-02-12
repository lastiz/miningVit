from sqladmin import ModelView
from wtforms.validators import optional, length

from database.models import (
    PurchasedMachine,
    User,
    MasterReferral,
    Finance,
    Deposit,
    Income,
    Withdrawal,
    Machine,
    Advert,
)
from .formatters import FORMATTERS
from utils.security import SecurityHasher


class ModelView(ModelView):
    column_type_formatters = FORMATTERS
    can_export = False


class UserAdmin(ModelView, model=User):
    category = "User category"
    name = "User"
    name_plural = "Users"
    icon = "fa-solid fa-user"
    can_create = True
    can_edit = True
    can_delete = False
    can_view_details = True

    column_list = [
        User.id,
        User.username,
        User.email,
        User.telegram,
        User.is_active,
        User.is_admin,
        "created_at",
    ]
    column_searchable_list = [
        User.username,
        User.email,
        User.telegram,
    ]
    column_default_sort = [
        ("created_at", True),
    ]
    column_sortable_list = [
        User.username,
        User.email,
        "created_at",
    ]

    # EDIT
    form_excluded_columns = [
        "last_online",
        "updated_at",
        "created_at",
        "finance",
        "machines",
        "ap_address",
    ]
    form_args = {
        "telegram": {"validators": [optional()]},
        "note": {"validators": [optional()]},
        "password_hash": {
            "validators": [length(min=6, max=64)],
            "label": "Password",
        },
        "affiliate_code": {
            "validators": [length(min=10, max=10)],
        },
    }

    async def on_model_change(
        self, data: dict, model: User, is_created: bool, request
    ) -> None:
        """Logic for updating or creation password_hash ofr user model"""
        if is_created or not data["password_hash"].startswith("$2b$"):
            model.password_hash = SecurityHasher.get_password_hash(
                data["password_hash"]
            )
        else:
            model.password_hash = data["password_hash"]

        data.pop("password_hash", None)


class MasterReferralAdmin(ModelView, model=MasterReferral):
    category = "User category"
    name = "Master_Referral"
    name_plural = "Master_Referral"
    icon = "fa-solid fa-user-group"
    can_create = True
    can_edit = True
    can_delete = False
    can_view_details = True

    form_include_pk = True


class FinanceAdmin(ModelView, model=Finance):
    category = "Finance category"
    name = "Finance"
    name_plural = "Finance"
    icon = "fa-solid fa-coins"
    can_create = True
    can_edit = True
    can_delete = False
    can_view_details = True

    column_list = [
        Finance.id,
        Finance.user,
        Finance.balance,
        Finance.income,
        Finance.affiliate_income,
        Finance.wallet,
    ]

    # EDIT
    form_excluded_columns = [
        "deposits",
        "withdrawals",
        "incomes",
    ]
    form_args = {
        "wallet": {
            "validators": [optional()],
        },
        "balance": {
            "validators": [optional()],
        },
        "income": {
            "validators": [optional()],
        },
        "affiliate_income": {
            "validators": [optional()],
        },
    }
    form_ajax_refs = {
        "user": {
            "fields": ["username", "email", "telegram"],
            "page_size": 15,
        }
    }


class DepositAdmin(ModelView, model=Deposit):
    category = "Finance category"
    name = "Deposit"
    name_plural = "Deposits"
    icon = "fa-solid fa-money-bill-trend-up"
    can_create = True
    can_edit = True
    can_delete = True
    can_view_details = True

    column_list = [
        "finance.user",
        Deposit.amount,
        Deposit.status,
        Deposit.platform,
        Deposit.created_at,
    ]
    column_labels = {
        "finance.user": "User",
    }
    column_searchable_list = [Deposit.status, Deposit.platform]
    column_sortable_list = [
        "created_at",
    ]
    column_default_sort = [
        ("created_at", True),
    ]

    # EDIT
    form_args = {
        "created_at": {"validators": [optional()]},
        "updated_at": {"validators": [optional()]},
    }


class WithdrawalAdmin(ModelView, model=Withdrawal):
    category = "Finance category"
    name = "Withdrawal"
    name_plural = "Withdrawals"
    icon = "fa-solid fa-stamp"
    can_create = True
    can_edit = True
    can_delete = True
    can_view_details = True

    column_list = [
        "finance.user",
        Withdrawal.amount,
        Withdrawal.status,
        Withdrawal.wallet,
        Withdrawal.created_at,
    ]
    column_labels = {
        "finance.user": "User",
    }
    column_searchable_list = [Withdrawal.status]
    column_sortable_list = [
        "created_at",
    ]
    column_default_sort = [
        ("created_at", True),
    ]

    # EDIT
    form_args = {
        "created_at": {"validators": [optional()]},
        "updated_at": {"validators": [optional()]},
    }


class IncomeAdmin(ModelView, model=Income):
    category = "Finance category"
    name = "Income"
    name_plural = "Incomes"
    icon = "fa-solid fa-money-bill-transfer"
    can_create = True
    can_edit = True
    can_delete = True
    can_view_details = True

    column_list = [
        "finance.user",
        Income.type,
        Income.amount,
        Income.status,
        Income.created_at,
    ]
    column_labels = {
        "finance.user": "User",
    }
    column_searchable_list = [
        Income.type,
        Income.status,
    ]
    column_sortable_list = [
        "created_at",
    ]
    column_default_sort = [
        ("created_at", True),
    ]

    # EDIT
    form_args = {
        "created_at": {"validators": [optional()]},
        "updated_at": {"validators": [optional()]},
    }
    form_ajax_refs = {"finance": {"fields": ["user_id", "id"]}}


class MachineAdmin(ModelView, model=Machine):
    category = "Machine category"
    name = "Machine"
    name_plural = "Machines"
    icon = "fa-solid fa-server"
    can_create = True
    can_edit = True
    can_delete = False
    can_view_details = True

    column_list = [
        Machine.id,
        Machine.title,
        Machine.coin,
        Machine.income,
        Machine.price,
    ]

    # EDIT
    form_excluded_columns = [
        "purchased",
    ]


class PurchasedMachineAdmin(ModelView, model=PurchasedMachine):
    category = "Machine category"
    name = "Purchased Machine"
    name_plural = "Purchased Machines"
    icon = "fa-solid fa-server"
    can_create = True
    can_edit = True
    can_delete = False
    can_view_details = True

    # LIST
    column_list = [
        PurchasedMachine.user,
        PurchasedMachine.created_at,
        PurchasedMachine.activated_time,
    ]

    # DETAILS
    column_details_exclude_list = [
        PurchasedMachine.user_id,
        PurchasedMachine.machine_id,
        PurchasedMachine.updated_at,
    ]

    # EDIT
    form_excluded_columns = ["created_at", "updated_at", "activated_time"]
    form_ajax_refs = {
        "user": {
            "fields": ["username", "email", "telegram"],
            "page_size": 15,
        }
    }


class AdvertAdmin(ModelView, model=Advert):
    name = "Advertising"
    name_plural = "Advertising"
    icon = "fa-brands fa-adversal"
    can_create = True
    can_edit = True
    can_delete = True
    can_view_details = True

    column_list = [
        Advert.id,
        Advert.title,
        Advert.body,
        Advert.is_visible,
    ]
    column_formatters = {
        Advert.body: lambda m, _: m.body[:70] + "..." if len(m.body) > 70 else m.body
    }
