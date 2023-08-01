# subelement.py
# interpret the Models.Stamp -> subelements -> args
# then change them to Main saved form.

from . import models

def stringify_bool(target):
    if target == False:
        return ''
    else:
        return 'T'

class Discrete_point():
    """
    # exchange_rate
        - subelement of pages, points, etc.
        - can add discrete value to the single stamp.
    Args
        name (str) : subelement's name param.
        lowerbound (int) : point's lower boundary. [lbound] '<=' [point]
        upperbound (int) : point's upper boundary. [point] '<' [ubound]
        is_accumulated (bool) : if True, accumulated value around all stamp's value will be saved. 
        acc_lbound (int) : accumulated value's lowerbound.
        acc_ubound (int) : accumulated value's upperbound.
    """

    # below is the type and args for set subelements, set subvars. 

    # selective for null OR valued params.
    # forced for MUST valued params.
    # private for MUST null params.


    # subelement_type is the input values for creation of stamp/subelement -> arg_names, arg_vals
    # all the values are selective.
    subelement_type = {
            'name': str, 
            'lowerbound' : int,
            'upperbound' : int,
            'is_accumulated' : bool,
            'acc_lbound' : int,
            'acc_ubound' : int,
        }
    
    # subvar_type is the input values for creation of main -> main_vals.
    subvar_type = {
        'value' : int, # forced 
        'accumulate' : int, # private
    }

    @classmethod
    def subelement_set(cls, name='point', lowerbound=-1000, upperbound=1000, is_accumulated=True, acc_lbound=-100000, acc_ubound=100000):
        """
        # subelement_set
            - Stamp model's subelement's datatype is all the string.
            - set method make settings to proper db affordable string. 
            - None value will be filled with preset value.
        
        Returns:
            - (dict) : string-only dict that can be put directly to the model.
        """

        # change type to properate form
        name = str(name)
        lowerbound = int(lowerbound)
        upperbound = int(upperbound)
        is_accumulated = bool(is_accumulated)
        acc_lbound = int(acc_lbound)
        acc_ubound = int(acc_ubound)

        # upper&under boundary's limit setting
        if lowerbound < -1000:
            lowerbound = -1000
        if upperbound > 1000:
            upperbound = 1000

        if acc_lbound < -100000:
            acc_lbound = -100000
        if acc_ubound > 100000:
            acc_ubound = 100000

        # casting types to string form
        name = str(name)
        lowerbound = str(lowerbound)
        upperbound = str(upperbound)
        is_accumulated = stringify_bool(is_accumulated)
        acc_lbound = str(acc_lbound)
        acc_ubound = str(acc_ubound)

        return {
            'name': name,
            'lowerbound' : lowerbound,
            'upperbound' : upperbound,
            'is_accumulated' : is_accumulated,
            'acc_lbound' : acc_lbound,
            'acc_ubound' : acc_ubound,
        }

    @classmethod
    def subelement_get(cls, target_queryset, *target_key):
        """
        # subelement_get
            - Stamp model's subelement's datatype is all the string.
            - get method changes some of them to the proper type then return.

        Args:
            - db_dict (dict) : string-only dict from db.
            - target_queryset (queryset) : object obtained from Stamp model. 
                + models.Stamp.objects.filter(< query for user_id & stamp_id & subelement_name & ~arg_name='' >)
        """
        # get args from queryset
        querydict = {}
        for obj in target_queryset:
            arg_name = getattr(obj, 'arg_name')
            arg_val = getattr(obj, 'arg_val')
            if arg_name != '' and arg_val != '':
                querydict[arg_name] = arg_val

        # validation of type
        for var in target_key:
            if type(var) != type(""):
                raise TypeError("target_key must be string list.")
        
        # result making
        result = []
        for var in target_key:
            typefunc = cls.subelement_type[var]
            result.append(typefunc(querydict[var]))
        
        return result

    @classmethod
    def subvar_set(cls, subelement_queryset, *value_list):
        """
        # subvar_set
            - Main model dosen't decide what subvars should put in the arg.
            - this function inspect the Stamp model's arg then decide the subvar instead.

        Args:
            - value (int) : value for discrete_point.
            - subelement_queryset (queryset) : object that targeted subelement is included, where from stamp model
                + you can obtain it like models.Stamp.objects.filter(< query for user_id & stamp_id & subelement_name & ~arg_name='' >)
        Returns:
            - (dict) result  : string-only dict that can directly put in Main model's subvar arg.
            - (bool)  : False will returned if the value is inapproate with Stamp model's subelement args. (like if value is over the upperbound value.)
        """

        # param validation
        value = value_list[0]
        try:
            value = int(value)
        except Exception:
            raise TypeError("value should be able to converted to the integer.")
        

        # get args from queryset
        parsed_db = {}
        for obj in subelement_queryset:
            arg_name = getattr(obj, 'arg_name')
            typefunc = cls.subelement_type[arg_name]
            arg_val = typefunc(getattr(obj, 'arg_val'))
            if arg_name != '' and arg_val != '':
                parsed_db[arg_name] = arg_val


        result = {}

        # boundary validation
        if parsed_db['lowerbound'] > value:
            result['value'] = parsed_db['lowerbound']
        elif value >= parsed_db['upperbound']:
            result['value'] = parsed_db['upperbound']
        else:
            result['value'] = value

        # accumulated value calculation
        if parsed_db['is_accumulated'] == True:
            user_id = getattr(subelement_queryset[0], 'user_id')
            stamp_id = getattr(subelement_queryset[0], 'id')

            #find the records of user, with matching stamp_id
            filtered_recode = models.Main.objects.filter(user_id = user_id, stamp_id = stamp_id, arg_name='value')
            if filtered_recode.exists() == False:
                result['accumulate'] = 0
            else:
                count = filtered_recode.count()
                if count == 1:
                    result['accumulate'] = int(getattr(filtered_recode[0], 'arg_val'))
                else:
                    result['accumulate'] = int(getattr(filtered_recode.order_by('-date')[0], 'arg_val'))
        
            # accumulated value boundary validation
            acc_added = result['accumulate'] + result['value']
            if parsed_db['acc_lbound'] > acc_added:
                result['accumulate'] = parsed_db['acc_lbound'] - result['value']
            elif acc_added >= parsed_db['acc_ubound']:
                result['accumulate'] = parsed_db['acc_ubound'] - result['value']

        #stringify result
        stringified = {}
        for k, v in result.items():
            stringified[k] = str(v)

        return stringified
    
    @classmethod
    def subvar_get(cls, target_queryset, *target_key):
        """
        # subvar_get
            - Stamp model's subvar's datatype is all the string.
            - get method changes some of them to the proper type then return.

        Args:
            - db_dict (dict) : string-only dict from db.
            - target_queryset (queryset) : object obtained from Main model. 
                + models.Main.objects.filter(< query for user_id & stamp_id & date & ~arg_name='' >)
        """
        # get args from queryset
        querydict = {}
        for obj in target_queryset:
            arg_name = getattr(obj, 'arg_name')
            arg_val = getattr(obj, 'arg_val')
            querydict[arg_name] = arg_val

        # validation of type
        for var in target_key:
            if type(var) != type(""):
                raise TypeError("target_key must be string list.")
        
        # result making
        result = []
        for var in target_key:
            typefunc = cls.subvar_type[var]
            result.append(typefunc(querydict[var]))
        
        return result
    

loc = {
    "discrete_point" : Discrete_point,
}
