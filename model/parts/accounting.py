import model.constants as constants


def policy_validator_costs(params, substep, state_history, previous_state):
    # Parameters
    validator_percentage_distribution = params['validator_percentage_distribution']
    validator_hardware_costs_per_epoch = params['validator_hardware_costs_per_epoch']
    validator_cloud_costs_per_epoch = params['validator_cloud_costs_per_epoch']
    validator_third_party_costs_per_epoch = params['validator_third_party_costs_per_epoch']

    # State Variables
    eth_price = previous_state['eth_price']
    number_of_validators = previous_state['number_of_validators']
    total_online_validator_rewards = previous_state['total_online_validator_rewards']

    # Calculate hardware, cloud, and third-party costs per validator type
    validator_count_distribution = number_of_validators * validator_percentage_distribution
    validator_hardware_costs = validator_count_distribution * validator_hardware_costs_per_epoch
    validator_cloud_costs = validator_count_distribution * validator_cloud_costs_per_epoch
    validator_third_party_costs = validator_percentage_distribution * validator_third_party_costs_per_epoch * total_online_validator_rewards / constants.gwei * eth_price

    # Calculate total validator costs per validator type and total network costs
    validator_costs = validator_hardware_costs + validator_cloud_costs + validator_third_party_costs
    total_network_costs = validator_costs.sum(axis=0)

    return {
        'validator_count_distribution': validator_count_distribution,
        'validator_hardware_costs': validator_hardware_costs,
        'validator_cloud_costs': validator_cloud_costs,
        'validator_third_party_costs': validator_third_party_costs,
        'validator_costs': validator_costs,
        'total_network_costs': total_network_costs
    }

def policy_calculate_yields(params, substep, state_history, previous_state):
    # Parameters
    validator_percentage_distribution = params['validator_percentage_distribution']

    # State Variables
    eth_price = previous_state['eth_price']
    eth_staked = previous_state['eth_staked']

    validator_costs = previous_state['validator_costs']
    total_network_costs = previous_state['total_network_costs']
    total_online_validator_rewards = previous_state['total_online_validator_rewards']
    validator_count_distribution = previous_state['validator_count_distribution']
    average_effective_balance = previous_state['average_effective_balance']

    # Calculate the aggregate metrics per validator type
    validator_eth_staked = validator_count_distribution * average_effective_balance / constants.gwei
    validator_revenue = validator_percentage_distribution * total_online_validator_rewards / constants.gwei * eth_price
    validator_profit = validator_revenue - validator_costs
    validator_revenue_yields = validator_revenue * constants.epochs_per_year / (eth_staked * eth_price)
    validator_profit_yields = validator_profit * constants.epochs_per_year / (eth_staked * eth_price)
    
    # Calculate the total metrics
    total_revenue = validator_revenue.sum(axis=0)
    total_profit = total_revenue - total_network_costs
    total_revenue_yields = validator_revenue_yields.sum(axis=0)
    total_profit_yields = validator_profit_yields.sum(axis=0)

    return {
        # TODO move ETH staked
        # Per validator
        'validator_eth_staked': validator_eth_staked,
        'validator_revenue': validator_revenue,
        'validator_profit': validator_profit,
        'validator_revenue_yields': validator_revenue_yields,
        'validator_profit_yields': validator_profit_yields,
        # Aggregate
        'total_revenue': total_revenue,
        'total_profit': total_profit,
        'total_revenue_yields': total_revenue_yields,
        'total_profit_yields': total_profit_yields,
    }

def update_total_online_validator_rewards(params, substep, state_history, previous_state, policy_input):
    # State Variables
    validating_rewards = previous_state['validating_rewards']
    whistleblower_rewards = previous_state['whistleblower_rewards']
    validating_penalties = previous_state['validating_penalties']
    total_tips_to_validators = previous_state['total_tips_to_validators']

    # Calculate total rewards for online validators
    total_online_validator_rewards = validating_rewards + whistleblower_rewards - validating_penalties + total_tips_to_validators

    return 'total_online_validator_rewards', total_online_validator_rewards
